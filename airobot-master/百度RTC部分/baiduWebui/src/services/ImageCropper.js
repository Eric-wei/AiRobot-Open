/**
 * @description 图片裁剪服务类
 */
class ImageCropper {
  /**
   * 裁剪视频帧中的指定区域到 Canvas
   * @param {HTMLVideoElement} videoElement 视频元素
   * @param {HTMLCanvasElement} targetCanvas 用于绘制裁剪后图像的目标 Canvas
   * @param {object} captureArea 裁剪区域信息 { x, y, width, height } (相对于视频显示尺寸)
   * @returns {Promise<void>} 操作完成的 Promise
   */
  async cropVisibleArea(videoElement, targetCanvas, captureArea) {
    return new Promise((resolve, reject) => {
      if (!videoElement || !targetCanvas || !captureArea) {
        return reject(new Error('缺少必要的参数'));
      }

      const videoWidth = videoElement.videoWidth;
      const videoHeight = videoElement.videoHeight;
      const displayWidth = videoElement.offsetWidth;
      const displayHeight = videoElement.offsetHeight;

      if (!videoWidth || !videoHeight || !displayWidth || !displayHeight) {
          return reject(new Error('无法获取视频尺寸信息'));
      }

      // 计算视频原生分辨率相对于显示尺寸的缩放比例
      const scaleX = videoWidth / displayWidth;
      const scaleY = videoHeight / displayHeight;

      // 将显示尺寸上的裁剪区域坐标和尺寸，转换为视频原生分辨率下的坐标和尺寸
      const sourceX = captureArea.x * scaleX;
      const sourceY = captureArea.y * scaleY;
      const sourceWidth = captureArea.width * scaleX;
      const sourceHeight = captureArea.height * scaleY;

      // 设置目标 Canvas 的尺寸为裁剪后的尺寸
      targetCanvas.width = sourceWidth;
      targetCanvas.height = sourceHeight;

      const context = targetCanvas.getContext('2d');
      if (!context) {
          return reject(new Error('无法获取 Canvas 上下文'));
      }

      // 清除之前的绘制 (虽然通常是新的绘制，但以防万一)
      context.clearRect(0, 0, targetCanvas.width, targetCanvas.height);

      // 从视频帧的指定区域绘制到目标 Canvas 的 (0, 0) 位置
      try {
        context.drawImage(
          videoElement,
          sourceX,        // 源图像中的 X 坐标
          sourceY,        // 源图像中的 Y 坐标
          sourceWidth,    // 源图像中要裁剪的宽度
          sourceHeight,   // 源图像中要裁剪的高度
          0,              // 目标 Canvas 上的 X 坐标
          0,              // 目标 Canvas 上的 Y 坐标
          sourceWidth,    // 在目标 Canvas 上绘制的宽度
          sourceHeight    // 在目标 Canvas 上绘制的高度
        );
        resolve(); // 绘制成功
      } catch (error) {
        console.error("drawImage 失败:", error);
        reject(error); // 绘制失败
      }
    });
  }
}

export default ImageCropper;