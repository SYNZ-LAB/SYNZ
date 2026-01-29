using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

[RequireComponent(typeof(AudioSource))]
public class SimpleAudioPlayer : MonoBehaviour
{
    private AudioSource audioSource;
    public static SimpleAudioPlayer Instance { get; private set; }
    public float CurrentVolume { get; private set; }

    void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(this.gameObject);
        }
        else
        {
            Instance = this;
        }
        audioSource = GetComponent<AudioSource>();
    }

    void Update()
    {
        if (audioSource.isPlaying)
        {
            float[] data = new float[256];
            audioSource.GetOutputData(data, 0);
            float sum = 0;
            foreach (var s in data) sum += s * s;
            CurrentVolume = Mathf.Sqrt(sum / 256.0f);
        }
        else
        {
            CurrentVolume = 0f;
        }
    }

    public void PlayFromFile(string absolutePath)
    {
        StartCoroutine(LoadAndPlay(absolutePath));
    }

    IEnumerator LoadAndPlay(string path)
    {
        // 1. Sanitize Path (Unity hates backslashes in URIs)
        path = path.Replace("\\", "/");
        
        // 2. Ensure Protocol
        string eventUrl;
        if (!path.StartsWith("file://"))
        {
             // Handle "C:/..." vs "/Users/..."
             if (!path.StartsWith("/")) 
                eventUrl = "file:///" + path; // file:///C:/Path...
             else
                eventUrl = "file://" + path;
        }
        else
        {
            eventUrl = path;
        }

        // Debug.Log($"[AudioPlayer] Loading: {eventUrl}"); # Optional Debug

        // Debug.Log($"[AudioPlayer] Loading: {eventUrl}"); # Optional Debug

        using (UnityWebRequest www = UnityWebRequestMultimedia.GetAudioClip(eventUrl, AudioType.MPEG)) # Force MPEG
        {
            yield return www.SendWebRequest();

            if (www.result == UnityWebRequest.Result.ConnectionError || www.result == UnityWebRequest.Result.ProtocolError)
            {
                Debug.LogError($"[AudioPlayer] Load Error for '{eventUrl}': {www.error}");
            }
            else
            {
                AudioClip clip = DownloadHandlerAudioClip.GetContent(www);
                if (clip != null && clip.loadState == AudioDataLoadState.Loaded)
                {
                    Debug.Log($"[AudioPlayer] Playing Clip: {clip.length}s");
                    audioSource.clip = clip;
                    audioSource.Play();
                }
                else
                {
                    Debug.LogWarning($"[AudioPlayer] Clip loaded but invalid or empty.");
                }
            }
        }
    }
}
