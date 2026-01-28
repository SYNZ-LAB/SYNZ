using System;
using System.IO;
using System.IO.Pipes;
using System.Text;
using System.Threading;
using UnityEngine;
using System.Collections.Concurrent;

public class NeuroLinkClient : MonoBehaviour
{
    private NamedPipeClientStream pipeClient;
    private Thread listenerThread;
    private bool isRunning = false;
    private ConcurrentQueue<string> messageQueue = new ConcurrentQueue<string>(); // Thread-safe queue

    void Start()
    {
        StartConnection();
    }

    void StartConnection()
    {
        listenerThread = new Thread(ConnectAndListen);
        listenerThread.IsBackground = true;
        listenerThread.Start();
    }

    void ConnectAndListen()
    {
        while (true) // Auto-reconnect loop
        {
            try
            {
                pipeClient = new NamedPipeClientStream(".", "SYNZ_NeuroLink", PipeDirection.InOut);
                Debug.Log("[NeuroLink] Attempting to connect to SYNZ Core...");
                
                pipeClient.Connect(5000); // 5 sec timeout
                Debug.Log("<color=green>[NeuroLink] Connected to Brain!</color>");
                
                isRunning = true;
                
                using (StreamReader reader = new StreamReader(pipeClient))
                {
                    while (pipeClient.IsConnected && isRunning)
                    {
                        string line = reader.ReadLine();
                        if (line != null)
                        {
                            // Enqueue for main thread
                            messageQueue.Enqueue(line);
                        }
                    }
                }
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[NeuroLink] Connection lost/failed: {e.Message}. Retrying in 2s...");
                Thread.Sleep(2000);
            }
            finally
            {
                if (pipeClient != null) pipeClient.Dispose();
            }
        }
    }

    void Update()
    {
        // Process messages on the Main Unity Thread (Required for UI/Animation)
        while (messageQueue.TryDequeue(out string message))
        {
            ProcessThought(message);
        }
    }

    void ProcessThought(string thought)
    {
        // 1. Parse Emotion Tags: [HAPPY] Hello there!
        string emotion = "NORMAL";
        string cleanText = thought;

        if (thought.Contains("[") && thought.Contains("]"))
        {
            try {
                int start = thought.IndexOf("[");
                int end = thought.IndexOf("]");
                if (end > start)
                {
                    emotion = thought.Substring(start + 1, end - start - 1).ToUpper(); // Extract "HAPPY"
                    cleanText = thought.Remove(start, end - start + 1).Trim(); // Remove "[HAPPY]"
                }
            } catch { /* Ignore parse errors */ }
        }

        // 2. Send to Live2D Controller
        // We find the controller in the scene (created by Bootstrap)
        var live2D = FindObjectOfType<CubismSYNZController>(); 
        if (live2D != null)
        {
            live2D.SetEmotion(emotion);
        }

        Debug.Log($"<color=cyan>[SYNZ]: {cleanText}</color> <color=grey>({emotion})</color>");
    }

    void OnDestroy()
    {
        isRunning = false;
        if (pipeClient != null) pipeClient.Dispose();
        if (listenerThread != null) listenerThread.Abort(); 
    }
}
