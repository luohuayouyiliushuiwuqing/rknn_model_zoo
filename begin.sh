#!/bin/bash
source activate rk-yolov8

export WEIGHT_BASE_ROOT="/home/igs/yhj_demo/v8/runs"

# 定义环境变量
export WEIGHT_ROOT="$WEIGHT_BASE_ROOT/Drone_mixout73/train_server/yolov8/weights"
#export WEIGHT_ROOT="/home/igs/yhj_demo/v8/runs/Dronecoco55/train_small_opt/Dronecoco55_yolov8_small1/weights"

export RKNN_ROOT="/home/igs/yhj_demo/RknnProjects/Projects/rknn_model_zoo/"
export ONNX_PATH="$WEIGHT_ROOT/export_rknn.onnx"
export RKNN_PATH="$WEIGHT_ROOT/export_rknn.rknn"
export RKNN_MIXING_ACCURACY_PATH="$WEIGHT_ROOT/export_rknn_mixing_accuracy.rknn"
export DATASET_PATH="$RKNN_ROOT/datasets/new_data/dataset_outdoor.txt"

#cd examples/yolov8/python
#rm -rf check*
#rm -rf export_rknn*
#rm -rf snapshot_*
#
#python convert.py  --onnx_path $ONNX_PATH --dataset $DATASET_PATH
#
#python mixing_accuracy1.py  --onnx_path $ONNX_PATH --dataset $DATASET_PATH
#python mixing_accuracy2.py --out_rknn_path $RKNN_PATH

echo "igs"|sudo -S rm -rf build install

cd /home/igs/yhj_demo/RknnProjects/Projects/rknn_model_zoo
echo "igs"|sudo -S bash ./build-linux.sh \
          -p $RKNN_PATH  \
          -c $RKNN_MIXING_ACCURACY_PATH \
          -v $RKNN_ROOT/examples/yolov8/model/dataset.txt \
          -i $RKNN_ROOT/examples/yolov8/model/img/img026.jpg \
          -t rk3588 \
          -a aarch64 \
          -d yolov8

scp  -r $RKNN_ROOT/install root@192.168.1.37:/root/Project/rknn_model_zoo/install

## 下面是在服务器上运行，root@192.168.254.198，密码root，
ssh root@192.168.1.37 <<EOF
# rm -rf /root/Project/rknn_model_zoo/install
cd /root/Project/rknn_model_zoo/install/rk3588_linux_aarch64/rknn_yolov8_demo/
export LD_LIBRARY_PATH=./lib
./rknn_yolov8_demo model/export_rknn.rknn model/img026.jpg
#./rknn_yolov8_demo_zero_copy model/export_rknn.rknn model/img026.jpg
./rknn_yolov8_demo model/export_rknn_mixing_accuracy.rknn model/img026.jpg
#./rknn_yolov8_demo_zero_copy model/export_rknn_mixing_accuracy.rknn model/img026.jpg
rm -rf /root/Project/rknn_model_zoo/install
EOF

echo "igs"|sudo -S rm -rf build install

