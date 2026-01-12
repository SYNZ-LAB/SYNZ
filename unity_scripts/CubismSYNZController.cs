using UnityEngine;
using Live2D.Cubism.Core;
using Live2D.Cubism.Framework;

/// <summary>
/// SYNZ Controller for Live2D
/// Attaches to the root of the Live2D Model Prefab.
/// Listens to NeuroLinkClient for emotion tags and drives Cubism Parameters.
/// </summary>
public class CubismSYNZController : MonoBehaviour
{
    [Header("References")]
    public CubismModel model;
    
    [Header("Current State")]
    [Range(0, 1)] public float MouthOpen = 0f;
    [Range(0, 1)] public float EyeOpen = 1f;
    [Range(0, 1)] public float Blush = 0f;

    // Parameter References (Found automatically)
    private CubismParameter _paramMouthOpen;
    private CubismParameter _paramEyeLOpen;
    private CubismParameter _paramEyeROpen;
    private CubismParameter _paramCheek;

    void Start()
    {
        if (model == null) model = GetComponent<CubismModel>();
        
        // Find parameters by ID (Standard Live2D IDs)
        // Note: IDs might vary by model (e.g. ParamMouthOpenY vs ParamMouthForm)
        var parameters = model.Parameters;
        _paramMouthOpen = parameters.FindById("ParamMouthOpenY");
        _paramEyeLOpen = parameters.FindById("ParamEyeLOpen");
        _paramEyeROpen = parameters.FindById("ParamEyeROpen");
        _paramCheek = parameters.FindById("ParamCheek");
    }

    void LateUpdate()
    {
        // 1. Mouth Flapping (Simple "Talk" simulation)
        // In a real app, use Audio Analysis (OVRLipSync)
        if (MouthOpen > 0)
        {
            float flap = Mathf.PerlinNoise(Time.time * 20f, 0f); // Fast random movement
            if (_paramMouthOpen != null) _paramMouthOpen.Value = flap * MouthOpen;
        }
        else
        {
             if (_paramMouthOpen != null) _paramMouthOpen.Value = 0;
        }

        // 2. Eyes (Blinking)
        if (_paramEyeLOpen != null) _paramEyeLOpen.Value = EyeOpen;
        if (_paramEyeROpen != null) _paramEyeROpen.Value = EyeOpen;

        // 3. Emotions (Blush)
        if (_paramCheek != null) _paramCheek.Value = Blush;
    }

    // Called by NeuroLinkClient when parsing a tag
    public void SetEmotion(string emotion)
    {
        Debug.Log($"[Live2D] Setting Emotion: {emotion}");
        switch (emotion.ToUpper())
        {
            case "HAPPY":
            case "SHY":
                Blush = 1.0f;
                break;
            case "ANGRY":
                // Set ParamBrowAngry...
                break;
            case "NORMAL":
                Blush = 0f;
                break;
        }
    }

    // Called by NeuroLinkClient when specific text is spoken
    public void SetTalking(bool isTalking)
    {
        MouthOpen = isTalking ? 1.0f : 0.0f;
    }
}
