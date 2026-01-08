using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;

class LilithIntegrationTest
{
    static async Task Main()
    {
        Console.WriteLine("🚀 Starting Project Lilith Integration Test...");
        
        int watcherPort = 5005;
        int bodyPort = 5006;
        
        // 1. Start Mock Body (Unity Overlay)
        var bodyTask = Task.Run(() => {
            using (UdpClient listener = new UdpClient(bodyPort))
            {
                Console.WriteLine("🎭 [The Body] Standing by for Action Tokens...");
                IPEndPoint groupEP = new IPEndPoint(IPAddress.Any, bodyPort);
                byte[] bytes = listener.Receive(ref groupEP);
                string response = Encoding.UTF8.GetString(bytes);
                Console.WriteLine($"✨ [The Body] SUCCESS! Received Action: {response}");
                Console.WriteLine("🎬 [The Body] Triggering Live2D Expression: SURPRISE");
            }
        });

        // 2. Start Mock Brain (PyTorch SLM)
        var brainTask = Task.Run(() => {
            using (UdpClient listener = new UdpClient(watcherPort))
            {
                Console.WriteLine("🧠 [The Brain] Neural Network initialized. Listening for Log Events...");
                IPEndPoint groupEP = new IPEndPoint(IPAddress.Any, watcherPort);
                byte[] bytes = listener.Receive(ref groupEP);
                string error = Encoding.UTF8.GetString(bytes);
                Console.WriteLine($"🔍 [The Brain] Detected Log Event: {error}");
                
                Console.WriteLine("🧠 [The Brain] Running Inference...");
                // Simulate Brain Processing
                string action = "{\"action\": \"SURPRISE\"}";
                byte[] sendBytes = Encoding.UTF8.GetBytes(action);
                using (UdpClient sender = new UdpClient())
                {
                    sender.Send(sendBytes, sendBytes.Length, "127.0.0.1", bodyPort);
                    Console.WriteLine($"📡 [The Brain] Dispatched Action Token to Body: {action}");
                }
            }
        });

        await Task.Delay(1500); // Give services time to "boot"

        // 3. Start Mock Watcher (C++ Sentinel)
        using (UdpClient sender = new UdpClient())
        {
            Console.WriteLine("👁️  [The Watcher] Monitoring Editor.log...");
            string errorMsg = "{\"type\": \"error\", \"content\": \"NullReferenceException: Object reference not set...\"}";
            byte[] sendBytes = Encoding.UTF8.GetBytes(errorMsg);
            
            Console.WriteLine("⚠️  [The Watcher] ERROR DETECTED in Unity Log!");
            sender.Send(sendBytes, sendBytes.Length, "127.0.0.1", watcherPort);
            Console.WriteLine("📡 [The Watcher] Sent Error Signal to Brain.");
        }

        await Task.WhenAll(bodyTask, brainTask);
        Console.WriteLine("\n✅ Integration Test Completed Successfully!");
        Console.WriteLine("All IPC channels (Watcher -> Brain -> Body) are functional.");
    }
}
