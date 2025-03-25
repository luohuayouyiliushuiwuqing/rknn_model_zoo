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
        goto out;
    }

    image_buffer_t src_image;
    memset(&src_image, 0, sizeof(image_buffer_t));
    ret = read_image(image_path, &src_image);

    if (ret != 0) {
        printf("main read image fail! ret=%d image_path=%s\n", ret, image_path);
        goto out;
    }

    object_detect_result_list od_results;

    ret = inference_yolov8_model(&rknn_app_ctx, &src_image, &od_results);
    if (ret != 0) {
        printf("init_yolov8_model fail! ret=%d\n", ret);
        goto out;
    }

    // 画框和概率
    for (int i = 0; i < od_results.count; i++) {
        object_detect_result *det_result = &(od_results.results[i]);
        printf("\033[31m%s (%d %d %d %d) %.3f\033[0m  ", coco_cls_to_name(det_result->cls_id),
               det_result->box.left, det_result->box.top,
               det_result->box.right, det_result->box.bottom,
               det_result->prop);
        // int x1 = det_result->box.left;
        // int y1 = det_result->box.top;
        // int x2 = det_result->box.right;
        // int y2 = det_result->box.bottom;


        // draw_rectangle(&src_image, x1, y1, x2 - x1, y2 - y1, COLOR_BLUE, 3);
        // sprintf(text, "%s %.1f%%", coco_cls_to_name(det_result->cls_id), det_result->prop * 100);
        // draw_text(&src_image, text, x1, y1 - 20, COLOR_RED, 10);
    }

    // write_image("out.png", &src_image);

out:
    deinit_post_process();

    ret = release_yolov8_model(&rknn_app_ctx);
    if (ret != 0) {
        printf("release_yolov8_model fail! ret=%d\n", ret);
    }
    if (src_image.virt_addr != NULL) {
        free(src_image.virt_addr);
    }

    // 记录程序结束时间
    struct timeval end_time;
    gettimeofday(&end_time, NULL);

    // 计算并打印程序执行时间
    double time_spent =( (end_time.tv_sec - start_time.tv_sec) + (end_time.tv_usec - start_time.tv_usec) / 1e6) * 1000;
    printf("\033[31mTotal time: %.3f ms\033[0m\n", time_spent);

    return 0;
}