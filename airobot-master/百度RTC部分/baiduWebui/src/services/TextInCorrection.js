
class TextInCorrector {
    // --------------------------------------------------------------------
    // 特别注意
    // --------------------------------------------------------------------
    // 在客户端/浏览器端储存 x-ti-app-id 和 x-ti-secret-code 是一件风险极大的事情
    // 极易造成 x-ti-app-id 和 x-ti-secret-code 的泄露。
    // 非特殊情况，请勿在客户端/浏览器存储 x-ti-app-id 和 x-ti-secret-code
    // 本示例代码仅供演示参考，请勿直接用于生产环境。

    #appId = '0bf2a74b934e4236f869ada18d35d387'; // 使用私有字段
    #secretCode = 'f2e266cacc2182db2a1b6721e6da21ba'; // 使用私有字段
    #apiUrl = 'https://api.textin.com/ai/service/v1/crop_enhance_image';

    constructor(appId, secretCode) {
        // 允许在实例化时覆盖默认的凭证（如果需要）
        // 但仍然强烈建议不要在客户端代码中硬编码这些值
        if (appId) this.#appId = appId;
        if (secretCode) this.#secretCode = secretCode;
    }

    /**
     * 发送图像文件或URL进行矫正
     * @param {File|string} imageSource - File对象或图像的URL
     * @returns {Promise<object>} - 返回包含API响应的Promise
     */
    correctImage(imageSource) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', this.#apiUrl);
            xhr.setRequestHeader('x-ti-app-id', this.#appId);
            xhr.setRequestHeader('x-ti-secret-code', this.#secretCode);

            xhr.onreadystatechange = () => {
                if (xhr.readyState === 4) {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        try {
                            const obj = JSON.parse(xhr.response);
                            console.log('API Response:', obj);
                            resolve(obj); // 成功时解析Promise
                        } catch (e) {
                            console.error('解析响应失败', e);
                            reject(new Error('解析响应失败')); // 失败时拒绝Promise
                        }
                    } else {
                        console.error('API请求失败:', xhr.status, xhr.statusText, xhr.response);
                        reject(new Error(`API请求失败: ${xhr.status} ${xhr.statusText}`)); // API错误时拒绝Promise
                    }
                }
            };

            xhr.onerror = () => {
                console.error('网络错误');
                reject(new Error('网络错误')); // 网络错误时拒绝Promise
            };

            if (imageSource instanceof File) {
                const reader = new FileReader();
                reader.readAsArrayBuffer(imageSource);
                reader.onload = () => {
                    xhr.setRequestHeader('Content-Type', 'application/octet-stream');
                    xhr.send(reader.result);
                };
                reader.onerror = (e) => {
                     console.error('读取文件失败', e);
                     reject(new Error('读取文件失败'));
                }
            } else if (typeof imageSource === 'string' && imageSource.trim() !== '') {
                xhr.setRequestHeader('Content-Type', 'text/plain');
                xhr.send(imageSource);
            } else {
                reject(new Error('无效的图像来源')); // 无效输入时拒绝Promise
            }
        });
    }
}
export default TextInCorrector; 
// 示例用法 (需要替换为实际的获取文件或URL的逻辑):
/*
async function handleCorrection() {
    const corrector = new TextInCorrector(); // 可以传入appId和secretCode覆盖默认值

    // --- 从文件输入获取 ---
    // const fileInput = document.querySelector('#file');
    // const file = fileInput.files[0];
    // if (file) {
    //     try {
    //         const result = await corrector.correctImage(file);
    //         console.log('矫正结果:', result);
    //         // 在这里处理成功的结果，例如显示图片
    //     } catch (error) {
    //         console.error('矫正失败:', error);
    //         // 在这里处理错误
    //     }
    // }

    // --- 从URL输入获取 ---
    // const urlInput = document.querySelector('#url');
    // const imageUrl = urlInput.value;
    // if (imageUrl) {
    //     try {
    //         const result = await corrector.correctImage(imageUrl);
    //         console.log('矫正结果:', result);
    //         // 在这里处理成功的结果
    //     } catch (error) {
    //         console.error('矫正失败:', error);
    //         // 在这里处理错误
    //     }
    // }
}
*/

// 如果你希望在其他模块中使用这个类，可以导出它
// export default TextInCorrector;


