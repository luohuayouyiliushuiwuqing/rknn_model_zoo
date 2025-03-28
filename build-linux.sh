#!/bin/bash
# GCC编译器路径设置
GCC_COMPILER=/home/igs/yhj_demo/RknnProjects/GCC/gcc-linaro-6.3.1-2017.05-x86_64_aarch64-linux-gnu/bin/aarch64-linux-gnu

set -e  # 出现错误时停止脚本

echo "$0 $@"  # 输出当前脚本名称及传递给脚本的参数

# 解析命令行参数
while getopts ":p:c:v:i:t:a:d:b:m:r" opt; do
  case $opt in
    p)  # 目标path 类型（例如 ）
      RKNN_PATH=$OPTARG
      ;;
    c)
      RKNN_MIXING_ACCURACY_PATH=$OPTARG
      ;;
    v)
      DATA_LABEL_PATH=$OPTARG
      ;;
    i)
      TEST_IMG_PATH=$OPTARG
      ;;
    t)  # 目标SOC类型（例如 rk3588、rk1808）
      TARGET_SOC=$OPTARG
      ;;
    a)  # 架构类型（例如 aarch64、armhf）
      TARGET_ARCH=$OPTARG
      ;;
    b)  # 构建类型（Debug/Release）
      BUILD_TYPE=$OPTARG
      ;;
    m)  # 是否启用Address Sanitizer（内存检查）
      ENABLE_ASAN=ON
      export ENABLE_ASAN=TRUE
      ;;
    d)  # 构建的demo名称（例如 yolov8）
      BUILD_DEMO_NAME=$OPTARG
      ;;
    r)  # 是否禁用RGA（图像处理，默认为启用）
      DISABLE_RGA=ON
      ;;
    :)  # 如果某个选项缺少参数
      echo "Option -$OPTARG requires an argument."
      exit 1
      ;;
    ?)
      echo "Invalid option: -$OPTARG index:$OPTIND"
      ;;
  esac
done

# 如果没有提供目标SOC或demo名称，打印错误信息并退出
if [ -z ${TARGET_SOC} ] || [ -z ${BUILD_DEMO_NAME} ]; then
  echo "$0 -t <target> -a <arch> -d <build_demo_name> [-b <build_type>] [-m]"
  echo ""
  echo "    -t : target (rk356x/rk3588/rk3576/rv1106/rk1808/rv1126)"
  echo "    -a : arch (aarch64/armhf)"
  echo "    -d : demo name"
  echo "    -b : build_type(Debug/Release)"
  echo "    -m : enable address sanitizer, build_type need set to Debug"
  echo "    -r : disable rga, use cpu resize image"
  echo "such as: $0 -t rk3588 -a aarch64 -d mobilenet"
  echo "Note: 'rk356x' represents rk3562/rk3566/rk3568, 'rv1106' represents rv1103/rv1106, 'rv1126' represents rv1109/rv1126"
  echo "Note: 'disable rga option is invalid for rv1103/rv1103b/rv1106"
  echo ""
  exit -1
fi

# 如果GCC编译器未设置，检查目标SOC并设置默认编译器
if [[ -z ${GCC_COMPILER} ]];then
    if [[ ${TARGET_SOC} = "rv1106"  || ${TARGET_SOC} = "rv1103" ]];then
        echo "Please set GCC_COMPILER for $TARGET_SOC"
        echo "such as export GCC_COMPILER=~/opt/arm-rockchip830-linux-uclibcgnueabihf/bin/arm-rockchip830-linux-uclibcgnueabihf"
        exit
    elif [[ ${TARGET_SOC} = "rv1109" || ${TARGET_SOC} = "rv1126" ]];then
        GCC_COMPILER=arm-linux-gnueabihf
    else
        GCC_COMPILER=aarch64-linux-gnu
    fi
fi
echo "$GCC_COMPILER"
export CC=${GCC_COMPILER}-gcc  # 设置C编译器
export CXX=${GCC_COMPILER}-g++  # 设置C++编译器

# 检查是否可以使用指定的编译器
if command -v ${CC} >/dev/null 2>&1; then
    :
else
    echo "${CC} is not available"
    echo "Please set GCC_COMPILER for $TARGET_SOC"
    echo "such as export GCC_COMPILER=~/opt/arm-rockchip830-linux-uclibcgnueabihf/bin/arm-rockchip830-linux-uclibcgnueabihf"
    exit
fi

# 默认构建类型为Release，如果没有指定则使用默认值
if [[ -z ${BUILD_TYPE} ]];then
    BUILD_TYPE=Release
fi

# 如果没有启用Address Sanitizer，则设置为OFF
if [[ -z ${ENABLE_ASAN} ]];then
    ENABLE_ASAN=OFF
fi

# 如果没有禁用RGA，则设置为OFF
if [[ -z ${DISABLE_RGA} ]];then
    DISABLE_RGA=OFF
fi

# 查找对应的demo路径
for demo_path in `find examples -name ${BUILD_DEMO_NAME}`
do
    if [ -d "$demo_path/cpp" ]
    then
        BUILD_DEMO_PATH="$demo_path/cpp"
        break;
    fi
done

# 如果没有找到demo路径，输出支持的demo并退出
if [[ -z "${BUILD_DEMO_PATH}" ]]
then
    echo "Cannot find demo: ${BUILD_DEMO_NAME}, only support:"

    for demo_path in `find examples -name cpp`
    do
        if [ -d "$demo_path" ]
        then
            dname=`dirname "$demo_path"`
            name=`basename $dname`
            echo "$name"
        fi
    done
    echo "rv1106_rv1103 only support: mobilenet and yolov5/6/7/8/x"
    exit
fi

# 处理目标SOC类型的映射，确保TARGET_SOC值是有效的
case ${TARGET_SOC} in
#    rk356x)
#        ;;
    rk3588)
        ;;
#    rv1106)
#        ;;
#    rv1103)
#        TARGET_SOC="rv1106"
#        ;;
#    rk3566)
#        TARGET_SOC="rk356x"
#        ;;
#    rk3568)
#        TARGET_SOC="rk356x"
#        ;;
#    rk3562)
#        TARGET_SOC="rk356x"
#        ;;
#    rk3576)
#        TARGET_SOC="rk3576"
#        ;;
#    rk1808)
#        TARGET_SOC="rk1808"
#        ;;
#    rv1109)
#        ;;
#    rv1126)
#        TARGET_SOC="rv1126"
#        ;;
    *)
        echo "Invalid target: ${TARGET_SOC}"
        echo "Valid target: rk3562,rk3566,rk3568,rk3588,rk3576,rv1106,rv1103,rk1808,rv1109,rv1126"
        exit -1
        ;;
esac

TARGET_SDK="rknn_${BUILD_DEMO_NAME}_demo"  # 设置SDK名称

TARGET_PLATFORM=${TARGET_SOC}_linux
if [[ -n ${TARGET_ARCH} ]];then
TARGET_PLATFORM=${TARGET_PLATFORM}_${TARGET_ARCH}
fi
ROOT_PWD=$( cd "$( dirname $0 )" && cd -P "$( dirname "$SOURCE" )" && pwd )  # 获取当前脚本所在目录的路径
INSTALL_DIR=${ROOT_PWD}/install/${TARGET_PLATFORM}/${TARGET_SDK}  # 安装目录
BUILD_DIR=${ROOT_PWD}/build/build_${TARGET_SDK}_${TARGET_PLATFORM}_${BUILD_TYPE}  # 构建目录

# 输出配置信息
echo "==================================="
echo "BUILD_DEMO_NAME=${BUILD_DEMO_NAME}"
echo "BUILD_DEMO_PATH=${BUILD_DEMO_PATH}"
echo "TARGET_SOC=${TARGET_SOC}"
echo "TARGET_ARCH=${TARGET_ARCH}"
echo "BUILD_TYPE=${BUILD_TYPE}"
echo "ENABLE_ASAN=${ENABLE_ASAN}"
echo "DISABLE_RGA=${DISABLE_RGA}"
echo "INSTALL_DIR=${INSTALL_DIR}"
echo "BUILD_DIR=${BUILD_DIR}"
echo "CC=${CC}"
echo "CXX=${CXX}"
echo "==============change begin=============="

echo "RKNN_PATH=${RKNN_PATH}"
echo "DATA_LABEL_PATH=${DATA_LABEL_PATH}"
echo "TEST_IMG_PATH=${TEST_IMG_PATH}"

echo "==============change end================"
echo "==================================="

# 如果构建目录不存在，创建该目录
if [[ ! -d "${BUILD_DIR}" ]]; then
  mkdir -p ${BUILD_DIR}
fi

# 如果安装目录已存在，删除它
if [[ -d "${INSTALL_DIR}" ]]; then
  rm -rf ${INSTALL_DIR}
fi

# 进入构建目录并开始构建
cd ${BUILD_DIR}
cmake ../../${BUILD_DEMO_PATH} \
    -DTARGET_SOC=${TARGET_SOC} \
    -DCMAKE_SYSTEM_NAME=Linux \
    -DCMAKE_SYSTEM_PROCESSOR=${TARGET_ARCH} \
    -DCMAKE_BUILD_TYPE=${BUILD_TYPE} \
    -DENABLE_ASAN=${ENABLE_ASAN} \
    -DDISABLE_RGA=${DISABLE_RGA} \
    -DCMAKE_INSTALL_PREFIX=${INSTALL_DIR} \
    -DRKNN_PATH=${RKNN_PATH} \
    -DRKNN_MIXING_ACCURACY_PATH=${RKNN_MIXING_ACCURACY_PATH} \
    -DDATA_LABEL_PATH=${DATA_LABEL_PATH} \
    -DTEST_IMG_PATH=${TEST_IMG_PATH}

make -j4  # 使用4个核心进行并行构建
make install  # 安装构建结果

# 检查安装目录中是否生成了rknn模型文件
suffix=".rknn"
shopt -s nullglob
if [ -d "$INSTALL_DIR" ]; then
    files=("$INSTALL_DIR/model/"/*"$suffix")
    shopt -u nullglob

    if [ ${#files[@]} -le 0 ]; then
        echo -e "\e[91mThe RKNN model can not be found in \"$INSTALL_DIR/model\", please check!\e[0m"
    fi
else
    echo -e "\e[91mInstall directory \"$INSTALL_DIR\" does not exist, please check!\e[0m"
fi
