#!/usr/bin/env python
# coding=utf-8
# vim:set fileencoding=utf-8:
"""
@Project ：rknn_model_zoo 
@File    ：mixing_accuracy1.py
@IDE     ：PyCharm 
@Author  ：高筱六和栾昊六
@Date    ：2025/3/5 10:50 
"""
import argparse

from rknn.api import RKNN

from colorchange import colorstr

DATASET_PATH = '../../../datasets/COCO/coco_subset_20.txt'  # 数据集路径的默认值
DEFAULT_QUANT = True  # 默认启用量化
PLATFORM = 'rk3588'  # 默认平台（用于模型部署）

# 定义函数用于解析命令行参数
def parse_arg():
    # 创建ArgumentParser对象，描述程序的功能
    parser = argparse.ArgumentParser(description="RKNN model conversion tool.")


    # 添加位置参数：模型路径，必须提供
    parser.add_argument('--onnx_path', type=str, help="Path to the ONNX model.")

    # 添加位置参数：平台类型，必须提供，支持的选择有一定限制
    parser.add_argument('--platform', type=str, default='rk3588',
                        choices=['rk3562', 'rk3566', 'rk3568', 'rk3576', 'rk3588', 'rk1808', 'rv1109', 'rv1126'],
                        help="Platform to deploy on.")

    # 添加可选参数：数据集路径，默认值为 DATASET_PATH
    parser.add_argument('--dataset', type=str, default=DATASET_PATH,
                        help="Path to the dataset file (optional).")

    # 解析命令行参数
    args = parser.parse_args()


    # 返回解析后的参数
    return args.onnx_path, args.platform, args.dataset


if __name__ == '__main__':

    print(colorstr("bright_red", "================== 混合量化提高精度 step 1 =================="))

    onnx_path, platform, dataset_path = parse_arg()

    print("=" * 60)
    print(f"ONNX 路径: {onnx_path}")
    print(f"平台: {platform}")
    print(f"数据集路径: {dataset_path}")
    print("=" * 60)

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

    # 使用hybrid_quantization_step 接口进行混合量化第一步
    rknn.hybrid_quantization_step1(
        dataset=dataset_path,  # 表示模型量化所需要的数据集
        # rknn_batch_size=-1,  # 表示自动调整模型输入batch数量
        # proposal=False,  # 设置为True，可以自动产生混合量化的配置建议，比较耗时
        proposal= True,  # 设置为True，可以自动产生混合量化的配置建议，比较耗时
        proposal_dataset_size=1,  # 第三步骤所用的图片
    )
    rknn.release()

