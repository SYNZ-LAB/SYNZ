using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;
using System.Collections.Concurrent;

public class NeuroLinkClient : MonoBehaviour
{
    private UdpClient udpClient;
    private Thread listenerThread;
    private bool isRunning = false;
    private ConcurrentQueue<string> messageQueue = new ConcurrentQueue<string>();

    private const string FACE_IP = "127.0.0.1";
    private const int FACE_PORT = 8005;

    void Start()
    {
        StartConnection();
    }

    void StartConnection()
    {
        try 
        {
            // Bind to ANY available port
            udpClient = new UdpClient(0); 
            udpClient.Client.ReceiveTimeout = 1000; // 1s timeout to check for shutdown
            
            Debug.Log($"[NeuroLink] UDP Socket created on Port {((IPEndPoint)udpClient.Client.LocalEndPoint).Port}");

            // Send Handshake
            Send("Unity Connected");

            listenerThread = new Thread(ListenLoop);
            listenerThread.IsBackground = true;
            listenerThread.Start();
            isRunning = true;
        }
        catch (Exception e)
        {
            Debug.LogError($"[NeuroLink] Failed to start UDP: {e.Message}");
        }
    }

    void ListenLoop()
    {
        IPEndPoint remoteEP = new IPEndPoint(IPAddress.Any, 0);
        while (isRunning)
        {
            try
            {
                if (udpClient.Available > 0) 
                {
                    byte[] data = udpClient.Receive(ref remoteEP);
                    string message = Encoding.UTF8.GetString(data);
                    messageQueue.Enqueue(message);
                }
                else
                {
                    Thread.Sleep(10); // Don't burn CPU
                }
            }
            catch (SocketException) 
            {
                // Timeout is normal
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[NeuroLink] Receive Error: {e.Message}");
            }
        }
    }

    void Send(string message)
    {
        try
        {
            byte[] data = Encoding.UTF8.GetBytes(message);
            udpClient.Send(data, data.Length, FACE_IP, FACE_PORT);
        }
        catch (Exception e)
        {
            Debug.LogError($"[NeuroLink] Send Error: {e.Message}");
        }
    }

    void Update()
    {
        // 1. Keep Alive (Heartbeat) every 5 seconds?
        // Actually face_server just needs one ping. But re-pinging is safer.
        if (Time.frameCount % 300 == 0) // Roughly every 5s at 60fps
        {
            Send("Unity Connected");
        }

        // 2. Process Messages
        while (messageQueue.TryDequeue(out string message))
        {
            ProcessThought(message);
        }
    }

    void ProcessThought(string thought)
    {
        // Ignore "ACK"
        if (thought == "ACK") return;

        // [AUDIO] Trigger
        if (thought.StartsWith("[AUDIO]"))
        {
            string audioPath = thought.Substring(7).Trim();
            PlayAudio(audioPath);
            return;
        }

        // 1. Extraction Logic
        string emotion = "NORMAL";
        string cleanText = thought;

        if (thought.Contains("[") && thought.Contains("]"))
        {
            try {
                int start = thought.IndexOf("[");
                int end = thought.IndexOf("]");
                if (end > start)
                {
                    string tag = thought.Substring(start + 1, end - start - 1);
                    if (tag == "HAPPY" || tag == "SAD" || tag == "ANGRY" || tag == "SURPRISED")
                    {
                        emotion = tag;
                        cleanText = thought.Remove(start, end - start + 1).Trim();
                    }
                }
            } catch { }
        }

        // 2. Send to Live2D Controller
        var live2D = FindFirstObjectByType<SYNZLive2DController>(); // Using proper class name
        if (live2D != null)
        {
            live2D.SetEmotion(emotion);
        }

        Debug.Log($"<color=cyan>[SYNZ]: {cleanText}</color> <color=grey>({emotion})</color>");
    }

    void PlayAudio(string path)
    {
        var player = GetComponent<SimpleAudioPlayer>();
        if (player != null)
        {
            Debug.Log($"[NeuroLink] Playing Audio: {path}");
            player.PlayFromFile(path);
        }
        else
        {
            // Fallback: Try to find on ANY object
            player = FindFirstObjectByType<SimpleAudioPlayer>();
            if (player != null) player.PlayFromFile(path);
            else Debug.LogWarning("[NeuroLink] No SimpleAudioPlayer found!");
        }
    }

    void OnDestroy()
    {
        isRunning = false;
        if (udpClient != null) udpClient.Close();
        if (listenerThread != null && listenerThread.IsAlive) listenerThread.Abort();
    }
}
