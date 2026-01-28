# Live2D Integration Guide 🎎

Since you already have the Cubism SDK and a `.moc3` model in Unity, here is the script you need to bridge SYNZ to the model.

## 1. The Strategy
We need to control the **parameters** of the Live2D model based on signals from `NeuroLinkClient`.
Specifically: `ParamMouthOpenY`.

## 2. The Script (`Live2DController.cs`)

Create a new C# script in Unity and attach it to the **root** of your Live2D prefab.

### Key Namespaces
You need `Live2D.Cubism.Core` to access the model parameters.

```csharp
using UnityEngine;
using Live2D.Cubism.Core; // IMPORTANT
using Live2D.Cubism.Framework;
```

### The Variables
You need a reference to the specific parameter for the mouth.

```csharp
private CubismModel _model;
private CubismParameter _mouthOpenParam;
public float sensitivity = 2.0f;
```

### `Start()`
Find the parameter by ID.

```csharp
void Start() {
    _model = this.GetComponent<CubismModel>();
    // Find the parameter by its ID (Standard ID is ParamMouthOpenY)
    _mouthOpenParam = _model.Parameters.FindById("ParamMouthOpenY");
}
```

### `LateUpdate()` (Animation Loop)
Live2D updates in `LateUpdate`. You must override the value *after* the animation plays.

```csharp
void LateUpdate() {
    // 1. Get Audio Volume from NeuroLink (You need to expose this from your Client script)
    float volume = NeuroLinkClient.Instance.CurrentVolume; 

    // 2. Apply to Mouth
    if (_mouthOpenParam != null) {
        float targetOpen = Mathf.Clamp01(volume * sensitivity);
        _mouthOpenParam.Value = targetOpen; 
    }
}
```

## 3. Connecting to NeuroLink
Your existing `NeuroLinkClient.cs` needs to expose `CurrentVolume`.
Make sure it calculates the RMS (Root Mean Square) of the audio being played by the AudioSource.

```csharp
// In NeuroLinkClient.cs
public float CurrentVolume { get; private set; }

void Update() {
    // Basic Audio analysis
    float[] data = new float[256];
    audioSource.GetOutputData(data, 0);
    float sum = 0;
    foreach(var s in data) sum += s * s;
    CurrentVolume = Mathf.Sqrt(sum / 256.0f);
}
```

## 4. Testing
1.  Run the Scene.
2.  Make SYNZ speak (`!run` something).
3.  The Live2D mouth should open when audio plays!
