using UnityEngine;
using Live2D.Cubism.Core;

/// <summary>
/// The "One-Click" Setup script for SYNZ in Unity.
/// Drop this on an empty GameObject, and it will auto-configure everything.
/// </summary>
public class SYNZ_Bootstrap : MonoBehaviour
{
    void Awake()
    {
        SetupSystem();
        SetupLive2D();
    }

    void SetupSystem()
    {
        // 1. Check if System exists, if not, create it
        GameObject systemObj = GameObject.Find("[SYNZ_SYSTEM]");
        if (systemObj == null)
        {
            systemObj = new GameObject("[SYNZ_SYSTEM]");
            DontDestroyOnLoad(systemObj);
            Debug.Log("[SYNZ] Generated [SYNZ_SYSTEM] Manager.");
        }

        // 2. Add NeuroLink (Network)
        if (systemObj.GetComponent<NeuroLinkClient>() == null)
        {
            systemObj.AddComponent<NeuroLinkClient>();
            Debug.Log("[SYNZ] Attached NeuroLinkClient.");
        }

        // 3. Add Audio Player (Voice)
        if (systemObj.GetComponent<SimpleAudioPlayer>() == null)
        {
            var audioPlayer = systemObj.AddComponent<SimpleAudioPlayer>();
            
            // Configure AudioSource
            var source = systemObj.GetComponent<AudioSource>();
            if (source == null) source = systemObj.AddComponent<AudioSource>();
            
            source.playOnAwake = false;
            source.loop = false;
            source.spatialBlend = 0f; // 2D Sound (Hear it everywhere)
            
            Debug.Log("[SYNZ] Attached SimpleAudioPlayer + AudioSource.");
        }
    }

    void SetupLive2D()
    {
        // 4. Find Live2D Model in Scene
        // We look for any object with a "CubismModel" component
        CubismModel model = FindObjectOfType<CubismModel>();
        
        if (model != null)
        {
            // Check if it has our controller
            if (model.gameObject.GetComponent<Live2DController>() == null)
            {
                model.gameObject.AddComponent<Live2DController>();
                Debug.Log($"[SYNZ] Found Model '{model.name}' -> Attached Live2DController.");
            }
            else
            {
                Debug.Log($"[SYNZ] Model '{model.name}' already has a Controller.");
            }
        }
        else
        {
            Debug.LogWarning("[SYNZ] No Live2D Model found in scene! (Drag your .moc3 prefab in!)");
        }
    }
}
