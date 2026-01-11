using UnityEngine;
using System.Collections;

public class AutoCrash : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        Debug.Log("Initializing Auto-Crash Sequence...");
        StartCoroutine(CrashRoutine());
    }

    IEnumerator CrashRoutine()
    {
        // Wait 3 seconds so everything loads first
        yield return new WaitForSeconds(3.0f);
        
        Debug.LogError("ReferenceMissingException: 'PlayerController' is not assigned in the Inspector!");
        Debug.LogError("NullReferenceException: Object reference not set to an instance of an object at GameHandler.cs:42");
    }
}
