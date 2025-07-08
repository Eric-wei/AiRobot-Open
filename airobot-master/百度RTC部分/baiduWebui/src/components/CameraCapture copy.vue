<template>
  <div v-if="show" class="camera-capture-overlay">
    <div class="camera-capture-content">
      <!-- Wrapper for video and overlay -->
      <div class="video-wrapper">
        <video ref="videoElement" autoplay playsinline class="camera-video" v-show="!capturedImage"></video>
        <canvas ref="overlayCanvasElement" class="overlay-canvas" v-show="!capturedImage"></canvas>
        <img v-if="correctedImage || capturedImage" :src="correctedImage || capturedImage" class="captured-image-preview" />
      </div>
      <canvas ref="canvasElement" style="display: none;"></canvas> <!-- Hidden canvas for capture -->
      <div class="controls">
        <button v-if="!sendImage" @click="captureImage" :disabled="!isCameraReady">拍照</button>
        <button v-if="sendImage" @click="confirmImage" :disabled="isProcessing">确认</button>
        <button v-if="sendImage" @click="retakeImage" :disabled="isProcessing">重新拍照</button>
        <button  @click="closeCamera">取消</button>
      </div>
      <p v-if="errorMsg" class="error-message">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted, defineProps, defineEmits, watch, nextTick } from 'vue';
import TextInCorrector from '../services/TextInCorrection';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  }
});
const textInCorrector = new TextInCorrector(); 
const emit = defineEmits(['close', 'image-captured']);

const videoElement = ref(null);
const canvasElement = ref(null); // Hidden canvas for final capture
const overlayCanvasElement = ref(null); // Visible overlay canvas
const stream = ref(null);
const isCameraReady = ref(false);
const errorMsg = ref('');
const scanLineY = ref(0); // Y position of the scan line within the capture area
const animationFrameId = ref(null); // To store the requestAnimationFrame ID
const isProcessing = ref(false); // 是否正在矫正图片
const capturedImage = ref(null); // 拍照后保存base64图片
const sendImage = ref(null); // 发送图片
const correctedImage = ref(null); // 新增：矫正后图片

// Function to draw the capture area overlay (no changes needed here for the base)
const drawCaptureAreaOverlay = (ctx, canvasWidth, canvasHeight) => {
  // Define the capture area size (e.g., 80% of the canvas)
  const captureWidth = canvasWidth * 0.8;
  const captureHeight = canvasHeight * 0.8; // You might want a specific aspect ratio

  // Calculate the top-left corner coordinates for centering
  const x = (canvasWidth - captureWidth) / 2;
  const y = (canvasHeight - captureHeight) / 2;

  // Clear previous drawings
  ctx.clearRect(0, 0, canvasWidth, canvasHeight);

  // Set fill style for the dark overlay
  ctx.fillStyle = 'rgba(0, 0, 0, 0.7)'; // Semi-transparent dark gray

  // Draw the overlay covering the whole canvas
  ctx.fillRect(0, 0, canvasWidth, canvasHeight);

  // Clear the central rectangle (making it transparent)
  // This effectively "cuts out" the capture area from the dark overlay
  ctx.clearRect(x, y, captureWidth, captureHeight);

  // Optional: Draw a border around the clear capture area for visibility
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.7)'; // Semi-transparent white
  ctx.lineWidth = 2;
  ctx.strokeRect(x, y, captureWidth, captureHeight);

  // Return capture area dimensions for the animation function
  return { x, y, width: captureWidth, height: captureHeight };
};

// Animation loop function
const animateScan = () => {
    if (!overlayCanvasElement.value || !isCameraReady.value) {
        // Stop animation if canvas is gone or camera stopped unexpectedly
        if (animationFrameId.value) cancelAnimationFrame(animationFrameId.value);
        animationFrameId.value = null;
        return;
    }
    const overlayCanvas = overlayCanvasElement.value;
    const overlayCtx = overlayCanvas.getContext('2d');
    const canvasWidth = overlayCanvas.width;
    const canvasHeight = overlayCanvas.height;

    // 1. Redraw the base overlay and get capture area dimensions
    const captureArea = drawCaptureAreaOverlay(overlayCtx, canvasWidth, canvasHeight);

    // 2. Calculate current absolute Y position of the scan line
    const lineY = captureArea.y + scanLineY.value;

    // 3. Draw the scanning line
    overlayCtx.strokeStyle = 'rgba(0, 255, 0, 0.7)'; // Semi-transparent green
    overlayCtx.lineWidth = 3; // Make the line a bit thicker
    overlayCtx.beginPath();
    overlayCtx.moveTo(captureArea.x, lineY);
    overlayCtx.lineTo(captureArea.x + captureArea.width, lineY);
    overlayCtx.stroke();

    // 4. Update line position for the next frame
    scanLineY.value += 2; // Adjust speed by changing this value

    // 5. Reset the line to the top if it goes past the bottom of the capture area
    if (scanLineY.value > captureArea.height) {
        scanLineY.value = 0;
    }

    // 6. Request the next frame
    animationFrameId.value = requestAnimationFrame(animateScan);
};


const startCamera = async () => {
  errorMsg.value = '';
  isCameraReady.value = false;
  // Clear overlay canvas when starting
  if (overlayCanvasElement.value) {
      const overlayCtx = overlayCanvasElement.value.getContext('2d');
      overlayCtx.clearRect(0, 0, overlayCanvasElement.value.width, overlayCanvasElement.value.height);
  }
  try {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      stream.value = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoElement.value && overlayCanvasElement.value) {
        const video = videoElement.value;
        const overlayCanvas = overlayCanvasElement.value;
        video.srcObject = stream.value;
        video.onloadedmetadata = () => {
          video.play(); // Ensure video plays
          isCameraReady.value = true;
          console.log('Camera ready.');

          // Match overlay canvas size to video display size
          // Use requestAnimationFrame to wait for layout calculation
          requestAnimationFrame(() => {
            const videoWidth = video.offsetWidth;
            const videoHeight = video.offsetHeight;
            overlayCanvas.width = videoWidth;
            overlayCanvas.height = videoHeight;
            const overlayCtx = overlayCanvas.getContext('2d');

            // Draw initial overlay
            drawCaptureAreaOverlay(overlayCtx, videoWidth, videoHeight);

            // Start the scanning animation
            scanLineY.value = 0; // Reset line position
            if (animationFrameId.value) { // Cancel any previous loop
                cancelAnimationFrame(animationFrameId.value);
            }
            animateScan(); // Start the new animation loop

            console.log(`Overlay canvas size set to: ${videoWidth}x${videoHeight}`);
          });
        };
        // Optional: Redraw overlay if video resizes (e.g., orientation change)
        // video.onresize = () => { ... redraw logic ... };
      }
    } else {
      throw new Error('浏览器不支持访问摄像头');
    }
  } catch (err) {
    console.error("Error accessing camera: ", err);
    errorMsg.value = `无法访问摄像头: ${err.message}`;
    stopCameraStream(); // Ensure stream is stopped on error
  }
};

const stopCameraStream = () => {
  // Stop the animation loop first
  if (animationFrameId.value) {
    cancelAnimationFrame(animationFrameId.value);
    animationFrameId.value = null;
  }

  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop());
    stream.value = null;
  }
  isCameraReady.value = false;
  if (videoElement.value) {
      videoElement.value.srcObject = null;
  }
   // Clear overlay canvas when stopping
  if (overlayCanvasElement.value) {
      const overlayCtx = overlayCanvasElement.value.getContext('2d');
      if (overlayCtx) {
        overlayCtx.clearRect(0, 0, overlayCanvasElement.value.width, overlayCanvasElement.value.height);
      }
  }
  console.log('Camera stream stopped and animation cancelled.');
};

// 辅助函数：将 base64 字符串转换为 File 对象
const base64ToFile = (base64String, fileName) => {
  const byteString = atob(base64String.split(',')[1] || base64String); // 处理可选的 data URI 前缀
  const mimeString = (base64String.split(',')[0] || '').split(':')[1]?.split(';')[0] || 'image/png'; // 尝试从 data URI 获取 MIME 类型，默认为 png
  const ab = new ArrayBuffer(byteString.length);
  const ia = new Uint8Array(ab);
  for (let i = 0; i < byteString.length; i++) {
    ia[i] = byteString.charCodeAt(i);
  }
  const blob = new Blob([ab], { type: mimeString });
  return new File([blob], fileName, { type: mimeString });
};


const captureImage = async () => {
  if (!isCameraReady.value || !videoElement.value || !canvasElement.value) return;
  const video = videoElement.value;
  const canvas = canvasElement.value;
  const context = canvas.getContext('2d');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  // 显示拍下的图片
  capturedImage.value = canvas.toDataURL('image/png');
  isProcessing.value = true;
  // 保持扫描动画不变（overlay和scan不隐藏），等待用户确认或重新拍照
  try {
    // base64转blob
    const blob = await (await fetch(capturedImage.value)).blob();
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const fileName = `capture-${timestamp}.png`;
    const file = new File([blob], fileName, { type: 'image/png' });
    const correctionResult = await textInCorrector.correctImage(file);
    if (correctionResult && correctionResult.result && correctionResult.result.image_list && correctionResult.result.image_list.length > 0) {
      const correctedBase64 = correctionResult.result.image_list[0].image;
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const fileName = `corrected-capture-${timestamp}.png`;
      sendImage.value = base64ToFile(correctedBase64, fileName);  
      correctedImage.value = 'data:image/png;base64,' + correctedBase64;
      errorMsg.value = '';   
    } else {
      errorMsg.value = "图片矫正失败，请重试。";
    }
  } catch (error) {
    errorMsg.value = `图片矫正出错: ${error.message}`;
  }
  isProcessing.value = false;
};

const confirmImage = async () => {
  if (isProcessing.value){
    errorMsg.value = '正在矫正图片...';
    return;
  }
  if (!sendImage.value) {
    errorMsg.value = '没有可发送图片。';
    return;
  }
  try {
      emit('image-captured', sendImage.value);
      closeCamera();
  } catch (error) {
    errorMsg.value = `发送图片出错: ${error.message}`;
  }
  
};

const retakeImage = () => {
  capturedImage.value = null;
  correctedImage.value = null;
  errorMsg.value = '';
  isProcessing.value = false;
  // 重新打开摄像头
  startCamera();
};

const closeCamera = () => {
  stopCameraStream();
  capturedImage.value = null;
  correctedImage.value = null;
  errorMsg.value = '';
  isProcessing.value = false;
  emit('close');
};

// 监听 props.show 的变化来启动/停止摄像头
watch(() => props.show, (newValue) => {
  if (newValue) {
    // 需要延迟一点时间确保DOM元素已渲染
    nextTick(() => {
        startCamera();
    });
  } else {
    stopCameraStream();
  }
}, { immediate: false }); // Don't run immediately on mount unless needed

onUnmounted(() => {
  // Ensure animation is stopped on unmount
  if (animationFrameId.value) {
    cancelAnimationFrame(animationFrameId.value);
    animationFrameId.value = null;
  }
  stopCameraStream(); // Cleanup on unmount
});

</script>

<style scoped>
.camera-capture-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1001;
}

.camera-capture-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  /* 修改尺寸 */
  height: 90vh; /* 高度为视口高度的90% */
  width: 60vh;  /* 宽度为高度的一半 */
  max-width: 95vw; /* 确保宽度不超过屏幕宽度 */
  max-height: 95vh;/* 确保高度不超过屏幕高度 */
  box-sizing: border-box; /* 包含 padding 和 border 在宽高内 */
  overflow: hidden; /* 防止内容溢出 */
}

.video-wrapper {
  position: relative; /* Crucial for absolute positioning of the overlay */
  width: 100%; /* Take full width of the content area */
  /* Let's use the video's intrinsic aspect ratio to help determine height if possible, or stick to the calculated height */
  height: calc(100% - 80px); /* Match video height calculation */
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 15px;
  background-color: #000;
  overflow: hidden;
}

.camera-video {
  /* Adjust video size */
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  display: block;
  /* Add position and z-index */
  position: relative; /* Establish stacking context */
  z-index: 0;       /* Ensure it's below the overlay */
}

.overlay-canvas {
  position: absolute;
  top: 0;
  left: 0;
  /* The JS will set the exact width/height matching the video's display size */
  width: 100%; /* Initial size, will be adjusted */
  height: 100%;/* Initial size, will be adjusted */
  pointer-events: none;
  z-index: 1; /* Ensure it's above the video (z-index: 0) */
}


.controls {
  display: flex;
  gap: 10px;
  margin-top: auto; /* 将按钮推到底部 */
  padding-bottom: 10px; /* 增加一些底部间距 */
}

.controls button {
  padding: 10px 20px;
  cursor: pointer;
}

.error-message {
    color: red;
    margin-top: 10px;
    font-size: 0.9em;
}
.captured-image-preview {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  display: block;
  margin: 0 auto;
}
</style>