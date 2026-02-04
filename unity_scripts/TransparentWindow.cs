using System;
using System.Runtime.InteropServices;
using UnityEngine;

public class TransparentWindow : MonoBehaviour
{
    [SerializeField] private Material m_Material; // Assign a material with specific shader if needed

    private struct MARGINS
    {
        public int cxLeftWidth;
        public int cxRightWidth;
        public int cyTopHeight;
        public int cyBottomHeight;
    }

    // Windows API Definitions
    [DllImport("user32.dll")]
    private static extern IntPtr GetActiveWindow();

    [DllImport("user32.dll")]
    private static extern int SetWindowLong(IntPtr hWnd, int nIndex, uint dwNewLong);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);

    [DllImport("Dwmapi.dll")]
    private static extern uint DwmExtendFrameIntoClientArea(IntPtr hWnd, ref MARGINS margins);

    // Constants
    const int GWL_STYLE = -16;
    const uint WS_POPUP = 0x80000000;
    const uint WS_VISIBLE = 0x10000000;
    const uint SWP_FRAMECHANGED = 0x0020;

    void Start()
    {
#if !UNITY_EDITOR
        // Transparent Window Setup logic
        IntPtr hWnd = GetActiveWindow();

        // 1. Remove Borders
        SetWindowLong(hWnd, GWL_STYLE, WS_POPUP | WS_VISIBLE);

        // 2. Extend Glass (Transparency)
        MARGINS margins = new MARGINS { cxLeftWidth = -1 };
        DwmExtendFrameIntoClientArea(hWnd, ref margins);
        
        // 3. Force Resize to Fullscreen (Fixes "Tiny Window")
        // Note: We use SWP_SHOWWINDOW (0x0040)
        int fWidth = Screen.currentResolution.width;
        int fHeight = Screen.currentResolution.height;
        SetWindowPos(hWnd, (IntPtr)(-1), 0, 0, fWidth, fHeight, 0x0040); // HWND_TOPMOST = -1
        
        // 4. Set Application Background
        Application.runInBackground = true;
#endif
    }

    void OnRenderImage(RenderTexture from, RenderTexture to)
    {
        Graphics.Blit(from, to, m_Material);
    }
}
