using UnityEngine;
using Live2D.Cubism.Core;
using Live2D.Cubism.Framework;

public class Live2DController : MonoBehaviour
{
    private CubismModel _model;
    
    // Parameters
    private CubismParameter _mouthOpenParam;
    private CubismParameter _breathParam;
    private CubismParameter _eyeLParam;
    private CubismParameter _eyeRParam;
    private CubismParameter _cheekParam; // [NEW]

    public float sensitivity = 3.0f; // Multiplier for audio volume
    [Range(0, 1)] public float Blush = 0f; // [NEW]
    
    // Blinking logic
    private float _blinkTimer;
    private float _nextBlinkTime;
    private bool _isBlinking;
    private float _blinkState; // 0 (Closed) -> 1 (Open)

    void Start()
    {
        _model = this.GetComponent<CubismModel>();
        
        // Find Parameters (Standard Live2D IDs)
        if (_model != null)
        {
            _mouthOpenParam = _model.Parameters.FindById("ParamMouthOpenY");
            _breathParam = _model.Parameters.FindById("ParamBreath");
            _eyeLParam = _model.Parameters.FindById("ParamEyeLOpen");
            _eyeRParam = _model.Parameters.FindById("ParamEyeROpen");
            _cheekParam = _model.Parameters.FindById("ParamCheek"); // [NEW]
        }
        
        ResetBlink();
    }

    void ResetBlink()
    {
        _blinkTimer = 0f;
        _isBlinking = false;
        _nextBlinkTime = Random.Range(2.0f, 6.0f); // Blink every 2-6 seconds
        _blinkState = 1.0f; // Open
    }

    // Cubism updates in LateUpdate, so we overwrite values here
    void LateUpdate()
    {
        if (_model == null) return;

        // --- 1. Lip Sync ---
        float volume = 0f;
        if (SimpleAudioPlayer.Instance != null)
        {
            volume = SimpleAudioPlayer.Instance.CurrentVolume;
        }

        if (_mouthOpenParam != null)
        {
            float targetOpen = Mathf.Clamp01(volume * sensitivity);
            _mouthOpenParam.Value = targetOpen;
        }

        // --- 2. Breathing ---
        // Simple sine wave for idle movement
        if (_breathParam != null)
        {
            float breath = (Mathf.Sin(Time.time * 1.5f) + 1f) * 0.5f; // 0 to 1
            _breathParam.Value = breath;
        }

    // --- 3. Blinking ---
        HandleBlinking();

        // --- 4. Emotion (Blush) ---
        if (_cheekParam != null) _cheekParam.Value = Blush;
    }

    void HandleBlinking()
    {
        if (_eyeLParam == null || _eyeRParam == null) return;

        _blinkTimer += Time.deltaTime;

        if (!_isBlinking)
        {
            // Waiting to blink
            if (_blinkTimer >= _nextBlinkTime)
            {
                _isBlinking = true;
                _blinkTimer = 0f;
            }
        }
        else
        {
            // Doing the blink (Closing then Opening)
            // Blink duration ~0.2s
            float t = _blinkTimer / 0.15f; 
            
            if (t <= 1.0f) {
                // Closing
                _blinkState = Mathf.Lerp(1.0f, 0.0f, t);
            } else if (t <= 2.0f) {
                // Opening
                _blinkState = Mathf.Lerp(0.0f, 1.0f, t - 1.0f);
            } else {
                // Done
                ResetBlink();
            }

            // Apply to eyes
            _eyeLParam.Value = _blinkState;
            _eyeRParam.Value = _blinkState;
        }
    }

    // Called by NeuroLinkClient
    public void SetEmotion(string emotion)
    {
        Debug.Log($"[Live2D] Setting Emotion: {emotion}");
        switch (emotion.ToUpper())
        {
            case "HAPPY":
            case "SHY":
                Blush = 1.0f;
                // Add Eye Smile logic here if desired
                break;
            case "NORMAL":
            default:
                Blush = 0f;
                break;
        }
    }
}