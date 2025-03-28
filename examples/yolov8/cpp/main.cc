#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>  // 包含 gettimeofday 函数

#include "yolov8.h"
#include "image_utils.h"
#include "file_utils.h"
#include "image_drawing.h"

/*-------------------------------------------
                  Main Function
-------------------------------------------*/
int main(int argc, char **argv) {
    if (argc != 3) {
        printf("%s <model_path> <image_path>\n", argv[0]);
        return -1;
    }

    // 记录程序开始时间
    struct timeval start_time;
    gettimeofday(&start_time, NULL);

    const char *model_path = argv[1];
    const char *image_path = argv[2];

    int ret;
    rknn_app_context_t rknn_app_ctx;
    memset(&rknn_app_ctx, 0, sizeof(rknn_app_context_t));

    init_post_process();

    ret = init_yolov8_model(model_path, &rknn_app_ctx);
    if (ret != 0) {
        printf("init_yolov8_model fail! ret=%d model_path=%s\n", ret, model_path);
        deinit_post_process();
        return ret;
    }

    image_buffer_t src_image;
    memset(&src_image, 0, sizeof(image_buffer_t));
    ret = read_image(image_path, &src_image);

    if (ret != 0) {
        printf("main read image fail! ret=%d image_path=%s\n", ret, image_path);
        release_yolov8_model(&rknn_app_ctx);
        deinit_post_process();
        return ret;
    }

    object_detect_result_list od_results;

    ret = inference_yolov8_model(&rknn_app_ctx, &src_image, &od_results);
    if (ret != 0) {
        printf("inference_yolov8_model fail! ret=%d\n", ret);
        free(src_image.virt_addr);
        release_yolov8_model(&rknn_app_ctx);
        deinit_post_process();
        return ret;
    }

    // 画框和概率
    for (int i = 0; i < od_results.count; i++) {
        object_detect_result *det_result = &(od_results.results[i]);
        printf("\033[31m%s (%d %d %d %d) %.3f\033[0m  ", coco_cls_to_name(det_result->cls_id),
               det_result->box.left, det_result->box.top,
               det_result->box.right, det_result->box.bottom,
               det_result->prop);
    }

    // 记录程序结束时间
    struct timeval end_time;
    gettimeofday(&end_time, NULL);

    // 计算并打印程序执行时间
    double time_spent =( (end_time.tv_sec - start_time.tv_sec) + (end_time.tv_usec - start_time.tv_usec) / 1e6) * 1000;
    printf("\033[31mTotal time: %.3f ms\033[0m\n", time_spent);

    // 清理资源
    free(src_image.virt_addr);
    release_yolov8_model(&rknn_app_ctx);
    deinit_post_process();

    return 0;
}