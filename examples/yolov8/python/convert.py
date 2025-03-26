# coding=utf-8
# vim:set fileencoding=utf-8:

import argparse
import glob
import os

from rknn.api import RKNN

from colorchange import colorstr

# 默认设置
DATASET_PATH = '../../../datasets/COCO/coco_subset_20.txt'  # 数据集路径的默认值
DEFAULT_RKNN_PATH = '../model/best/yolov8_rk3588.rknn'  # 转换后的RKNN模型默认输出路径
DEFAULT_QUANT = True  # 默认启用量化
PLATFORM = 'rk3588'  # 默认平台（用于模型部署）
ID = '9b526b9482fc5cc5'


# 定义函数用于解析命令行参数
def parse_arg():
    # 创建ArgumentParser对象，描述程序的功能
    parser = argparse.ArgumentParser(description="RKNN model conversion tool.")

    # 添加位置参数：模型路径，必须提供  #--all_model_path /home/igs/yhj_demo/v8/ultralytics-main-overfitting/runs/train/Drone3/weights \
    parser.add_argument('--all_model_path', type=str, help="Path to the ONNX model.")

    # 添加位置参数：模型路径，必须提供
    parser.add_argument('--onnx_path', type=str, help="Path to the ONNX model.")

    # 添加位置参数：平台类型，必须提供，支持的选择有一定限制
    parser.add_argument('--platform', type=str, default='rk3588',
                        choices=['rk3562', 'rk3566', 'rk3568', 'rk3576', 'rk3588', 'rk1808', 'rv1109', 'rv1126'],
                        help="Platform to deploy on.")

    parser.add_argument('--device_id', type=str, default=ID,
                        help="Path to save the converted RKNN model.")

    # 添加可选参数：量化类型，支持 'i8', 'u8', 'fp'，如果不传递则为 None
    parser.add_argument('--dtype', type=str, default='i8', choices=['i8', 'u8', 'fp'],
                        help="Quantization type (i8, u8, fp).")

    # 添加可选参数：输出路径，默认值为 DEFAULT_RKNN_PATH
    parser.add_argument('--output', type=str,
                        help="Path to save the converted RKNN model.")

    # 添加可选参数：数据集路径，默认值为 DATASET_PATH
    parser.add_argument('--dataset', type=str, default=DATASET_PATH,
                        help="Path to the dataset file (optional).")

    # 解析命令行参数
    args = parser.parse_args()

    # 根据传入的 dtype 参数决定是否启用量化
    if args.dtype is None:  # 如果没有指定 dtype，则使用默认量化设置
        do_quant = DEFAULT_QUANT
    elif args.dtype in ['i8', 'u8']:  # 如果 dtype 为 'i8' 或 'u8'，启用量化
        do_quant = True
    else:  # 如果 dtype 为 'fp'，则不启用量化
        do_quant = False

    # 如果没有指定 onnx_path 和 output，且 all_model_path 也没有提供
    if args.onnx_path is not None and args.output is None:
        # output_path = os.path.dirname(args.onnx_path)
        model_file = os.path.splitext(args.onnx_path)[0]  # 去除文件扩展名
        args.output = model_file + ".rknn"

    elif args.onnx_path is None and args.output is None:
        if args.all_model_path is None:
            print("Please specify at least one model path.")
            exit(1)
        # 查找 all_model_path 下的所有 .onnx 文件
        onnx_files = glob.glob(os.path.join(args.all_model_path, "*.onnx"))

        # 如果没有找到任何 .onnx 文件
        if not onnx_files:
            print(f"No ONNX models found in {args.all_model_path}")
            exit(1)

        # 如果只有一个 .onnx 文件，直接选择它
        if len(onnx_files) == 1:
            model_file = os.path.splitext(onnx_files[0])[0]  # 去除文件扩展名
            args.onnx_path = model_file + ".onnx"
            args.output = model_file + ".rknn"
        else:
            print(f"Found multiple ONNX models in {args.all_model_path}, please specify which one to use.")
            exit(1)

    # 返回解析后的参数
    return args.onnx_path, args.platform, args.device_id, do_quant, args.output, args.dataset


if __name__ == '__main__':

    print(colorstr("bright_red", "================== 正常ONNX转RKNN + 相关评估分析 =================="))

    onnx_path, platform, device_id, do_quant, output_path, dataset_path = parse_arg()

    print("=" * 30)
    print(f"ONNX 路径: {onnx_path}")
    print(f"平台: {platform}")
    print(f"ID: {device_id}")
    print(f"是否量化: {do_quant}")
    print(f"输出路径: {output_path}")
    print(f"数据集路径: {dataset_path}")
    print("=" * 30)

    # Create RKNN object
    rknn = RKNN(verbose=False)

    # Pre-process config
    print('--> Config model')
    rknn.config(mean_values=[[0, 0, 0]], std_values=[[255, 255, 255]], target_platform=platform)
    print('done')

    # Load model
    print('--> Loading model')
    ret = rknn.load_onnx(model=onnx_path)
    if ret != 0:
        print('Load model failed!')
        exit(ret)
    print('done')

    # Build model
    print('--> Building model')
    ret = rknn.build(do_quantization=do_quant, dataset=dataset_path)
    if ret != 0:
        print('Build model failed!')
        exit(ret)
    print('done')

    # Export rknn model
    print('--> Export rknn model')
    ret = rknn.export_rknn(output_path)
    if ret != 0:
        print('Export rknn model failed!')
        exit(ret)
    print('done')

    print(colorstr("bright_red", "==================精度分析=================="))

    rknn.accuracy_analysis(
        inputs=["/home/igs/yhj_demo/RknnProjects/Projects/rknn_model_zoo/datasets/new_data/dataset_outdoor/img019.jpg"],
        output_dir="./snapshot_convert",
        target=platform,
        device_id=device_id,
    )

    print(colorstr("bright_red", "==================性能评估的Debug模式=================="))

    # 使用init_runtime接口初始化运行环境
    rknn.init_runtime(
        target=platform,
        device_id=device_id,
        perf_debug=True,  # 表示是否开启性能评估的Debug模式
        eval_mem=True,  # 表示是否是内存评估
    )

    print(colorstr("bright_red", "==================内存评估=================="))
    # 使用eval_memory接口进行内存评估
    rknn.eval_memory(
        is_print=True,  # 表示使能打印内存评估信息
    )

    # Release
    rknn.release()
