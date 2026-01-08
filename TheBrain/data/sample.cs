using System;
using UnityEngine;

public class LilithController : MonoBehaviour {
    void Start() {
        Debug.Log("Hello World"); <ACTION_SMILE>
    }

    void Update() {
        if (Input.GetKeyDown(KeyCode.Space)) {
            Debug.LogError("Something went wrong!"); <ACTION_SURPRISE>
        }
    }
}
// Some C++ code too
#include <iostream>
int main() {
    std::cout << "Error here" << std::endl; <ACTION_THINK>
    return 0;
}
