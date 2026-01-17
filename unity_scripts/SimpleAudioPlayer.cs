using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

[RequireComponent(typeof(AudioSource))]
public class SimpleAudioPlayer : MonoBehaviour
{
    private AudioSource audioSource;

    void Awake()
    {
        audioSource = GetComponent<AudioSource>();
    }

    public void PlayFromFile(string absolutePath)
    {
        StartCoroutine(LoadAndPlay(absolutePath));
    }

    IEnumerator LoadAndPlay(string path)
    {
        // Unity needs "file://" prefix for local files
        string eventUrl = "file://" + path;
        
        using (UnityWebRequest www = UnityWebRequestMultimedia.GetAudioClip(eventUrl, AudioType.MPEG))
        {
            yield return www.SendWebRequest();

            if (www.result == UnityWebRequest.Result.ConnectionError || www.result == UnityWebRequest.Result.ProtocolError)
            {
                Debug.LogError($"[AudioPlayer] Load Error: {www.error}");
            }
            else
            {
                AudioClip clip = DownloadHandlerAudioClip.GetContent(www);
                if (clip != null)
                {
                    Debug.Log($"[AudioPlayer] Playing Clip: {clip.length}s");
                    audioSource.clip = clip;
                    audioSource.Play();
                    
                    // Optional: Lip Sync Hook
                    // OVRLipSync.Process(clip);
                }
            }
        }
    }
}
