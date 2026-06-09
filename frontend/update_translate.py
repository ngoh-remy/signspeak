import re

file_path = "c:\\Users\\lenovo\\Desktop\\SignSpeakL\\frontend\\src\\pages\\Translate.jsx"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Imports
content = content.replace("import './Translate.css';", "import './Translate.css';\nimport { Holistic } from '@mediapipe/holistic';")

# 2. Add refs
content = content.replace("const intervalRef = useRef(null);", "const intervalRef = useRef(null);\n  const holisticRef = useRef(null);\n  const reqAnimRef = useRef(null);")

# 3. Replace the Start Session interval logic
# Find where the interval is setup:
interval_regex = r"      const canvas = canvasRef\.current;.*?1\.0\); \/\/ 100% quality to prevent artifacting from confusing the CNN\n\s*\}\n\s*\}, 33\); \/\/ ~30 FPS — increased speed to capture 30 frames in 1 second"

new_mediapipe_logic = """
      // 3. Setup MediaPipe Holistic
      const holistic = new Holistic({
        locateFile: (file) => {
          return `https://cdn.jsdelivr.net/npm/@mediapipe/holistic/${file}`;
        }
      });

      holistic.setOptions({
        modelComplexity: 1,
        smoothLandmarks: true,
        enableSegmentation: false,
        smoothSegmentation: false,
        refineFaceLandmarks: false,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5
      });

      holistic.onResults((results) => {
        // Extract exactly 258 keypoints matching the Python backend
        let pose = new Array(33 * 4).fill(0);
        if (results.poseLandmarks) {
          results.poseLandmarks.forEach((res, i) => {
            pose[i * 4] = res.x;
            pose[i * 4 + 1] = res.y;
            pose[i * 4 + 2] = res.z;
            pose[i * 4 + 3] = res.visibility || 0;
          });
        }

        let lh = new Array(21 * 3).fill(0);
        if (results.leftHandLandmarks) {
          results.leftHandLandmarks.forEach((res, i) => {
            lh[i * 3] = res.x;
            lh[i * 3 + 1] = res.y;
            lh[i * 3 + 2] = res.z;
          });
        }

        let rh = new Array(21 * 3).fill(0);
        if (results.rightHandLandmarks) {
          results.rightHandLandmarks.forEach((res, i) => {
            rh[i * 3] = res.x;
            rh[i * 3 + 1] = res.y;
            rh[i * 3 + 2] = res.z;
          });
        }

        const keypoints = [...pose, ...lh, ...rh];

        // Send to backend
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({ type: 'keypoints', data: keypoints }));
        }
      });
      holisticRef.current = holistic;

      // 4. Send frames to MediaPipe
      const processVideo = async () => {
        if (videoRef.current && holisticRef.current && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          // Send current frame to holistic model
          await holisticRef.current.send({ image: videoRef.current });
        }
        // Loop as fast as possible
        reqAnimRef.current = requestAnimationFrame(processVideo);
      };

      videoRef.current.onloadeddata = () => {
        processVideo();
      };
"""

content = re.sub(interval_regex, new_mediapipe_logic, content, flags=re.DOTALL)

# 4. Stop Session cleanup
cleanup_regex = r"    if \(intervalRef\.current\) \{\n\s*clearInterval\(intervalRef\.current\);\n\s*intervalRef\.current = null;\n\s*\}"
new_cleanup = """    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    if (reqAnimRef.current) {
      cancelAnimationFrame(reqAnimRef.current);
      reqAnimRef.current = null;
    }
    if (holisticRef.current) {
      holisticRef.current.close();
      holisticRef.current = null;
    }"""
content = re.sub(cleanup_regex, new_cleanup, content, flags=re.DOTALL)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated Translate.jsx successfully.")
