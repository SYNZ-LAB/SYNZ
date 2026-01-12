using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;
using UnityEngine.UI;
using System.Runtime.InteropServices;

public class LilithOverlay : MonoBehaviour
{
    [Header("Network Settings")]
    public int listenPort = 5006; // Port to receive Action Tokens from Brain
    
    [Header("UI References")]
    public Image moodGlowImage; // Assign an image with a soft glow sprite

    [Header("Window Settings")]
    public bool makeTransparent = true;
    public bool clickThrough = true;

    private Thread receiveThread;
    private UdpClient client;
    private bool running = true;
    
    // ACTION STATE
    private bool isThinking = false;
    public float pulseSpeed = 5.0f;

    // Win32 API
    [DllImport("user32.dll")]
    private static extern IntPtr GetActiveWindow();
    [DllImport("user32.dll")]
    private static extern int SetWindowLong(IntPtr hWnd, int nIndex, uint dwNewLong);
    [DllImport("user32.dll")]
    private static extern uint GetWindowLong(IntPtr hWnd, int nIndex);
    [DllImport("user32.dll")]
    private static extern bool SetLayeredWindowAttributes(IntPtr hWnd, uint crKey, byte bAlpha, uint dwFlags);
    [DllImport("user32.dll")]
    private static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);

    private const int GWL_EXSTYLE = -20;
    private const uint WS_EX_LAYERED = 0x00080000;
    private const uint WS_EX_TRANSPARENT = 0x00000020;
    private const uint LWA_COLORKEY = 0x00000001;
    private const uint LWA_ALPHA = 0x00000002;
    private static readonly IntPtr HWND_TOPMOST = new IntPtr(-1);
    private const uint SWP_NOMOVE = 0x0002;
    private const uint SWP_NOSIZE = 0x0001;

    void Update()
    {
        // PULSE ANIMATION LOGIC
        if (isThinking && moodGlowImage != null)
        {
            // Ping-pong alpha between 0.3 and 1.0
            float alpha = Mathf.Lerp(0.3f, 1.0f, (Mathf.Sin(Time.time * pulseSpeed) + 1.0f) / 2.0f);
            Color c = moodGlowImage.color;
            c.a = alpha;
            moodGlowImage.color = c;
        }
        else if (!isThinking && moodGlowImage != null)
        {
            // Reset alpha when not thinking
            Color c = moodGlowImage.color;
            c.a = 1.0f;
            moodGlowImage.color = c;
        }
    }

    void Start()
    {
        if (makeTransparent && !Application.isEditor)
        {
            SetupWindow();
        }

        StartUdpReceiver();
    }

    void SetupWindow()
    {
        IntPtr hWnd = GetActiveWindow();
        
        // 1. Make window layeredss
        uint style = GetWindowLong(hWnd, GWL_EXSTYLE);
        SetWindowLong(hWnd, GWL_EXSTYLE, style | WS_EX_LAYERED);

        // 2. Make it transparent (chroma key or alpha)
        // Assuming the camera background is black (0,0,0) and we want to remove it
        // Or use LWA_ALPHA for global opacity
        // Here we use LWA_COLORKEY to make black pixels transparent
        SetLayeredWindowAttributes(hWnd, 0, 0, LWA_COLORKEY);

        // 3. Click-through
        if (clickThrough)
        {
            SetWindowLong(hWnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT);
        }

        // 4. Always on top
        SetWindowPos(hWnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE);
    }

    void StartUdpReceiver()
    {
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();
    }

    void ReceiveData()
    {
        client = new UdpClient(listenPort);
        while (running)
        {
            try
            {
                IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, 0);
                byte[] data = client.Receive(ref anyIP);
                string text = Encoding.UTF8.GetString(data);
                
                // Dispatch to main thread
                UnityMainThreadDispatcher.Instance().Enqueue(() => {
                    HandleMessage(text);
                });
            }
            catch (Exception e)
            {
                Debug.LogError(e.ToString());
            }
        }
    }

    void HandleMessage(string json)
    {
        Debug.Log("Received: " + json);
        // Parse JSON and trigger VTube Studio
        // Example: {"action": "SMILE", "intensity": 1.0}
        
        if (json.Contains("THINK"))
        {
            isThinking = true;
            UpdateUIMood(Color.yellow); // Thinking Color
        }
        else
        {
            isThinking = false; // Stop thinking for any other action
            
            if (json.Contains("SMILE"))
            {
                // Trigger VTS parameter
                VTSClient.Instance.TriggerExpression("Smile");
                UpdateUIMood(Color.cyan); // Happy/Helpful mood
            }
            else if (json.Contains("ANGRY"))
            {
                UpdateUIMood(Color.red); // Frustrated mood
            }
        }
        // ... handle other actions
    }

    void UpdateUIMood(Color moodColor)
    {
        // Change the mood glow color if assigned
        if (moodGlowImage != null)
        {
            moodGlowImage.color = moodColor;
        }
        Debug.Log("Switching UI Mood to: " + moodColor);
    }

    void OnApplicationQuit()
    {
        running = false;
        if (client != null) client.Close();
        if (receiveThread != null) receiveThread.Abort();
    }
}
