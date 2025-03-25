#!/usr/bin/env python
# coding=utf-8
# vim:set fileencoding=utf-8:
"""
@Project ：rknn_model_zoo 
@File    ：mixing_accuracy2.py
@IDE     ：PyCharm 
@Author  ：高筱六和栾昊六
@Date    ：2025/3/5 14:05 
"""
import argparse

from rknn.api import RKNN

from colorchange import colorstr

DEFAULT_QUANT = True  # 默认启用量化
PLATFORM = 'rk3588'  # 默认平台（用于模型部署）
ID='9b526b9482fc5cc5'

# 定义函数用于解析命令行参数
def parse_arg():
    # 创建ArgumentParser对象，描述程序的功能
    parser = argparse.ArgumentParser(description="RKNN model conversion tool.")

    # 添加位置参数：模型路径，必须提供
    parser.add_argument('--out_rknn_path', type=str, help="Path to the RKNN model.")

    # 添加位置参数：平台类型，必须提供，支持的选择有一定限制
    parser.add_argument('--platform', type=str, default='rk3588',
                        choices=['rk3562', 'rk3566', 'rk3568', 'rk3576', 'rk3588', 'rk1808', 'rv1109', 'rv1126'],
                        help="Platform to deploy on.")

    parser.add_argument('--device_id', type=str, default=ID,
                        help="Path to save the converted RKNN model.")

    # 解析命令行参数
    args = parser.parse_args()

    # 返回解析后的参数
    return args.out_rknn_path, args.platform, args.device_id


if __name__ == "__main__":
    print(colorstr("bright_red", "================== 混合量化提高精度 step 2 =================="))

    out_rknn_path, platform, device_id = parse_arg()

    print("=" * 60)
    print(f"OUT RKNN 路径: {out_rknn_path}")
    print(f"平台: {platform}")
    print(f"ID: {device_id}")
    print("=" * 60)

    rknn = RKNN(verbose=False)

    # 调用hyborid_quantization_step2接口进行混合量化的第二个步骤
    rknn.hybrid_quantization_step2(
        model_input="./export_rknn.model",  # 表示第一步生成的模型文件
        data_input="./export_rknn.data",  # 表示第一步生成的配置文件
        model_quantization_cfg="./export_rknn.quantization.cfg"  # 表示第一步生成的量化配置文件
    )

    # 调用量化精度分析接口（评估RKNN模型）
    rknn.accuracy_analysis(
        inputs=["/home/igs/yhj_demo/RknnProjects/Projects/rknn_model_zoo/datasets/new_data/dataset_outdoor/img019.jpg"],
        output_dir="./snapshot_mixing_accuracy",
        target=platform,
        device_id=device_id,
    )

    # 调用RKNN模型导出RKNN模型
    rknn.export_rknn(export_path=out_rknn_path.replace(".rknn", "_mixing_accuracy.rknn"))

    rknn.release()
