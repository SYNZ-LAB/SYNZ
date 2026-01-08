using UnityEngine;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System;

public class VTSClient : MonoBehaviour
{
    public static VTSClient Instance;
    private ClientWebSocket ws;
    private string vtsUri = "ws://localhost:8001";

    void Awake()
    {
        Instance = this;
        Connect();
    }

    async void Connect()
    {
        ws = new ClientWebSocket();
        try {
            await ws.ConnectAsync(new Uri(vtsUri), CancellationToken.None);
            Debug.Log("[VTS] Connected to VTube Studio");
        } catch (Exception e) {
            Debug.LogError($"[VTS] Connection failed: {e.Message}");
        }
    }

    public async void TriggerExpression(string expressionName)
    {
        if (ws == null || ws.State != WebSocketState.Open) return;

        Debug.Log($"[VTS] Triggering Expression: {expressionName}");
        
        // VTS API Message format (Simplified)
        string message = "{\"apiName\": \"VTubeStudioPublicAPI\", \"apiVersion\": \"1.0\", \"requestID\": \"SomeID\", \"messageType\": \"ExpressionActivationRequest\", \"data\": {\"expressionFile\": \"" + expressionName + ".exp3.json\", \"active\": true}}";
        
        byte[] bytes = Encoding.UTF8.GetBytes(message);
        await ws.SendAsync(new ArraySegment<byte>(bytes), WebSocketMessageType.Text, true, CancellationToken.None);
    }

    async void OnApplicationQuit()
    {
        if (ws != null) await ws.CloseAsync(WebSocketCloseStatus.NormalClosure, "Closing", CancellationToken.None);
    }
}
