using UnityEngine;

public class MainMenuManager : MonoBehaviour
{
    public GameObject mainCanvas;
    public GameObject modeCanvas;

    void Start()
    {
        // Start with only the MainCanvas active
        mainCanvas.SetActive(true);
        modeCanvas.SetActive(false);
    }

    public void ShowModeCanvas()
    {
        mainCanvas.SetActive(false);
        modeCanvas.SetActive(true);
    }

    public void ShowMainCanvas()
    {
        mainCanvas.SetActive(true);
        modeCanvas.SetActive(false);
    }
}
