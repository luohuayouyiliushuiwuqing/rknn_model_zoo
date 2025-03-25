cd examples/yolov8/python
python convert.py --all_model_path /home/igs/yhj_demo/v8/ultralytics-main-off/runs/train/exp/weights
cp /home/igs/yhj_demo/v8/ultralytics-main-off/runs/train/exp/weights/best.rknn /home/igs/yhj_demo/RknnProjects/Projects/rknn_model_zoo/examples/yolov8/python/model
cd /home/igs/yhj_demo/RknnProjects/Projects/rknn_model_zoo/examples/yolov8/python

scp  -r /home/igs/yhj_demo/RknnProjects/Projects/rknn_model_zoo/examples/yolov8/python root@192.168.254.198:/root/Project/rknn_model_zoo/examples/yolov8

## 下面是在服务器上运行，root@192.168.254.198，密码root，
ssh root@192.168.254.198 <<EOF
cd /root/Project/rknn_model_zoo/examples/yolov8/python
python yolov8.py --model_path /root/Project/rknn_model_zoo/examples/yolov8/python/model/best.rknn  --target rk3588 --img_folder /root/Project/rknn_model_zoo/examples/yolov8/python/img
EOF