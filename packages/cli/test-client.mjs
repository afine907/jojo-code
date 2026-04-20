import { spawn } from "child_process";
import { EventEmitter } from "events";

// 直接启动 Python Server 并测试
const pythonPath = "/tmp/nano-code/.venv/bin/python";
const pythonpath = "/tmp/nano-code/src";

async function main() {
  console.log("Testing TypeScript Client with correct Python...\n");
  
  return new Promise((resolve, reject) => {
    const process = spawn(pythonPath, ["-m", "nano_code.server.rpc"], {
      stdio: ["pipe", "pipe", "pipe"],
      env: { ...process.env, PYTHONPATH: pythonpath },
    });
    
    let buffer = "";
    
    process.stderr.on("data", (data) => {
      const msg = data.toString();
      if (msg.includes("started")) {
        console.log("1. ✅ Server started");
        
        // 发送请求
        const request = JSON.stringify({
          jsonrpc: "2.0",
          id: "1",
          method: "config.get",
          params: {}
        }) + "\n";
        
        process.stdin.write(request);
        console.log("2. ✅ Sent request");
      }
    });
    
    process.stdout.on("data", (data) => {
      buffer += data.toString();
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";
      
      for (const line of lines) {
        if (line.trim()) {
          try {
            const resp = JSON.parse(line);
            if (resp.result) {
              console.log("3. ✅ Got response:", JSON.stringify(resp.result));
              console.log("\n🎉 Test passed!");
              process.kill();
              resolve(0);
            }
          } catch (e) {}
        }
      }
    });
    
    process.on("exit", (code) => {
      if (code !== 0) {
        reject(new Error(`Server exited with code ${code}`));
      }
    });
    
    // 超时
    setTimeout(() => {
      process.kill();
      reject(new Error("Timeout"));
    }, 5000);
  });
}

main().catch(console.error);
