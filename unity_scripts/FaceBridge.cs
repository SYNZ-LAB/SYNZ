using System;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using UnityEngine;
using System.Collections.Concurrent;

public class FaceBridge : MonoBehaviour
{
    // Configuration
    public string faceServerIP = "127.0.0.1";
    public int faceServerPort = 8005;
    
    // Internal
    private UdpClient udpClient;
    private Thread receiveThread;
    private bool isRunning = false;
    private ConcurrentQueue<string> mainThreadQueue = new ConcurrentQueue<string>();
    
    // References
    public SimpleAudioPlayer audioPlayer; // Drag in Inspector

    void Start()
    {
        InitializeUDP();
        SendHello();
    }

    void InitializeUDP()
    {
        try
        {
            udpClient = new UdpClient();
            udpClient.Connect(faceServerIP, faceServerPort);
            
            isRunning = true;
            receiveThread = new Thread(ReceiveLoop);
            receiveThread.IsBackground = true;
            receiveThread.Start();
            
            Debug.Log($"[FaceBridge] Connected to {faceServerIP}:{faceServerPort}");
        }
        catch (Exception e)
        {
            Debug.LogError($"[FaceBridge] Failed to init UDP: {e.Message}");
        }
    }

    void SendHello()
    {
        SendChat("System: Unity Connected");
    }

    public void SendChat(string message)
    {
        if (udpClient == null) return;
        try
        {
            byte[] data = Encoding.UTF8.GetBytes(message);
            udpClient.Send(data, data.Length);
        }
        catch (Exception e)
        {
            Debug.LogError($"[FaceBridge] Send Error: {e.Message}");
        }
    }

    void ReceiveLoop()
    {
        IPEndPoint remoteEndPoint = new IPEndPoint(IPAddress.Any, 0);
        while (isRunning)
        {
            try
            {
                byte[] data = udpClient.Receive(ref remoteEndPoint);
                string text = Encoding.UTF8.GetString(data);
                mainThreadQueue.Enqueue(text);
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[FaceBridge] Receive Error (Thread): {e.Message}");
                // Break or continue? Continue for now.
            }
        }
    }

    void Update()
    {
        while (mainThreadQueue.TryDequeue(out string message))
        {
            ProcessMessage(message);
        }
    }

    void ProcessMessage(string msg)
    {
        // 1. Check for Audio Signal
        if (msg.StartsWith("[AUDIO]"))
        {
            string path = msg.Substring(7).Trim(); // Remove "[AUDIO] "
            Debug.Log($"<color=yellow>[FaceBridge] Audio Signal: {path}</color>");
            
            if (audioPlayer != null)
            {
                audioPlayer.PlayFromFile(path);
            }
            else
            {
                Debug.LogWarning("[FaceBridge] No AudioPlayer assigned!");
            }
        }
        // 2. Normal Chat
        else
        {
            Debug.Log($"<color=cyan>[SYNZ]: {msg}</color>");
            // TODO: Display in Text Bubble
        }
    }

    void OnDestroy()
    {
        isRunning = false;
        if (udpClient != null) udpClient.Close();
        if (receiveThread != null && receiveThread.IsAlive) receiveThread.Abort();
    }
}
