using UnityEngine;
using Live2D.Cubism.Core;
using Live2D.Cubism.Framework;

public class SYNZLive2DController : MonoBehaviour
{
    private CubismModel _model;
    
    // Parameters
    private CubismParameter _mouthOpenParam;
    private CubismParameter _mouthFormParam; // Controls smile/frown shape
    private CubismParameter _breathParam;
    private CubismParameter _eyeLParam;
    private CubismParameter _eyeRParam;
    private CubismParameter _cheekParam; 

    public float sensitivity = 8.0f; // Multiplier for audio volume
    [Range(0, 1)] public float Blush = 0f;
    
    // Blinking logic
    private float _blinkTimer;
    private float _nextBlinkTime;
    private bool _isBlinking;
    private float _blinkState; // 0 (Closed) -> 1 (Open)

    // Movement Logic
    private Vector3 _startPos;
    private float _jumpVelocity;
    private float _currentYOffset;
    private const float GRAVITY = -15.0f;
    private const float JUMP_FORCE = 0.6f; // How high to jump
    
    // Debug


    void Start()
    {
        _startPos = transform.localPosition;
        _model = this.GetComponent<CubismModel>();
        
        // ... (Parameter finding code remains the same) ...
        if (_model != null)
        {
            Debug.Log($"[Live2D] Scanning Model Parameters for '{_model.name}'...");
            Debug.Log($"[VISIBILITY] Pos: {transform.position}, Scale: {transform.localScale}, Layer: {gameObject.layer}");
            Debug.Log($"[VISIBILITY] Camera Pos: {Camera.main.transform.position}, Size: {Camera.main.orthographicSize}");
            
            // Force reasonable defaults if broken
            if (transform.localScale.x < 0.01f) {
                Debug.LogWarning("[FIX] Scale was too small! Resetting to 1.0");
                transform.localScale = Vector3.one;
            }
            _mouthOpenParam = _model.Parameters.FindById("ParamMouthOpenY");
            if (_mouthOpenParam == null) _mouthOpenParam = _model.Parameters.FindById("PARAM_MOUTH_OPEN_Y");
            if (_mouthOpenParam == null) _mouthOpenParam = _model.Parameters.FindById("ParamMouthOpen");
            
            _mouthFormParam = _model.Parameters.FindById("ParamMouthForm"); 

            if (_mouthOpenParam != null) Debug.Log($"[Live2D] Linked Mouth to: {_mouthOpenParam.Id}");
            else Debug.LogError("[Live2D] CRITICAL: Could not find Mouth Open Parameter!");

            _breathParam = _model.Parameters.FindById("ParamBreath");
            if (_breathParam == null) _breathParam = _model.Parameters.FindById("PARAM_BREATH");

            _eyeLParam = _model.Parameters.FindById("ParamEyeLOpen");
            _eyeRParam = _model.Parameters.FindById("ParamEyeROpen");
            
            _cheekParam = _model.Parameters.FindById("ParamCheek");
            if (_cheekParam == null) _cheekParam = _model.Parameters.FindById("PARAM_CHEEK");
        }
        
        // [FIX 3.0] Remove Crashing *StateMachineBehaviour* from Animator
        var animators = GetComponentsInChildren<Animator>();
        foreach (var anim in animators)
        {
            var behaviours = anim.GetBehaviours<StateMachineBehaviour>();
            foreach (var b in behaviours)
            {
                if (b.GetType().FullName.Contains("CubismFadeStateObserver") || b.GetType().Name == "CubismFadeStateObserver")
                {
                    Debug.LogWarning($"[SYNZ] Destroying crashing StateMachineBehaviour: {b.GetType().Name} on {anim.gameObject.name}");
                    DestroyImmediate(b); // Force immediate removal
                }
            }
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

    void HandleBlinking()
    {
        if (_eyeLParam == null || _eyeRParam == null) return;

        _blinkTimer += Time.deltaTime;

        if (!_isBlinking)
        {
            if (_blinkTimer >= _nextBlinkTime)
            {
                _isBlinking = true;
                _blinkTimer = 0f;
            }
        }
        else
        {
            float t = _blinkTimer / 0.15f; 
            
            if (t <= 1.0f) {
                _blinkState = Mathf.Lerp(1.0f, 0.0f, t);
            } else if (t <= 2.0f) {
                _blinkState = Mathf.Lerp(0.0f, 1.0f, t - 1.0f);
            } else {
                ResetBlink();
            }

            _eyeLParam.Value = _blinkState;
            _eyeRParam.Value = _blinkState;
        }
    }

    void LateUpdate()
    {
        if (_model == null) return;

        // --- Debug Input (Supports both Legacy and New Input System) ---
        bool pressM = false;
        bool pressJ = false;

#if ENABLE_INPUT_SYSTEM
        if (UnityEngine.InputSystem.Keyboard.current != null)
        {
            pressM = UnityEngine.InputSystem.Keyboard.current.mKey.isPressed;
            pressJ = UnityEngine.InputSystem.Keyboard.current.jKey.wasPressedThisFrame;
        }
#else
        pressM = Input.GetKey(KeyCode.M);
        pressJ = Input.GetKeyDown(KeyCode.J);
#endif

        if (pressM)
        {
            if (_mouthOpenParam != null) _mouthOpenParam.Value = 1.0f;
            if (_mouthFormParam != null) _mouthFormParam.Value = 1.0f; // Force Smile
            return; // Skip audio logic
        }

        if (pressJ) TriggerJump();

        // ... (Lip Sync & Breathing code remains same) ...

        // --- 1. Lip Sync ---
        float volume = 0f;
        if (SimpleAudioPlayer.Instance != null) volume = SimpleAudioPlayer.Instance.CurrentVolume;

        if (_mouthOpenParam != null)
        {
            float targetOpen = Mathf.Clamp(volume * sensitivity, 0f, 5.0f);
            _mouthOpenParam.Value = targetOpen;
            if (_mouthFormParam != null) _mouthFormParam.Value = 0.5f; 
        }

        // --- 2. Breathing ---
        if (_breathParam != null)
        {
            float breath = (Mathf.Sin(Time.time * 1.5f) + 1f) * 0.5f; 
            _breathParam.Value = breath;
        }

        // --- 3. Blinking ---
        HandleBlinking();
        
        // --- 4. Emotion (Blush) ---
        if (_cheekParam != null) _cheekParam.Value = Blush;

        // --- 5. VTuber Movement (Idle + Jump) ---
        UpdatePhysics();
    }

    void UpdatePhysics()
    {
        // 1. Idle Float (Subtle Bobbing)
        float idleY = Mathf.Sin(Time.time * 2.0f) * 0.02f; // +/- 0.02 units

        // 2. Jump Physics
        if (_jumpVelocity > 0 || _currentYOffset > 0)
        {
            _currentYOffset += _jumpVelocity * Time.deltaTime;
            _jumpVelocity += GRAVITY * Time.deltaTime;

            if (_currentYOffset < 0)
            {
                _currentYOffset = 0;
                _jumpVelocity = 0;
                // Landing wobble could go here
            }
        }

        // Apply
        transform.localPosition = _startPos + new Vector3(0, idleY + _currentYOffset, 0);
    }

    public void TriggerJump()
    {
        if (_currentYOffset <= 0.01f) // Don't double jump
        {
            _jumpVelocity = JUMP_FORCE;
        }
    }

    public void SetEmotion(string emotion)
    {
        Debug.Log($"[Live2D] Setting Emotion: {emotion}");
        switch (emotion.ToUpper())
        {
            case "HAPPY":
            case "EXCITED": // [NEW] Trigger Jump
                Blush = 1.0f;
                TriggerJump();
                break;
            case "SHY":
                Blush = 1.0f;
                break;
            case "NORMAL":
            default:
                Blush = 0f;
                break;
        }
    }
}