using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using System.Collections.Generic; // Add this line

public class CursorController : MonoBehaviour
{
    public SocketClient socketClient;
    public RectTransform cursorTransform; // Assign this in the Inspector
    public float hoverDuration = 2f; // Duration to hover before click
    private float hoverTimer = 0f;
    private Button hoveredButton = null;
    void Start()
    {
        if (socketClient == null)
        {
            socketClient = FindObjectOfType<SocketClient>();
            if (socketClient == null)
            {
                Debug.LogError("SocketClient is not assigned and not found in the scene.");
                return;
            }
        }
    }
    void Update()
    {
        if (socketClient != null)
        {
            string data = socketClient.Data;
            if (string.IsNullOrEmpty(data))
            {
                Debug.LogWarning("Received empty or null data from SocketClient.");
                return;
            }
            Debug.Log("Received Data: " + data);

            data = data.Replace("[", "").Replace("]", "");
            data = data.Replace("(", "").Replace(")", "");

            string[] points = data.Split(',');

            float x = 400 + float.Parse(points[18]) * -2;
            float y = 250 + -(float.Parse(points[19]) * 2);

            cursorTransform.localPosition = new Vector3(x, y, 0);

            // Check for hover and click
            CheckForHoverAndClick();
        }
    }

    void CheckForHoverAndClick()
    {
        PointerEventData pointerData = new PointerEventData(EventSystem.current)
        {
            position = cursorTransform.position
        };

        List<RaycastResult> results = new List<RaycastResult>(); // Add List<T> type
        EventSystem.current.RaycastAll(pointerData, results);

        foreach (RaycastResult result in results)
        {
            Button button = result.gameObject.GetComponent<Button>();
            if (button != null)
            {
                if (hoveredButton == button)
                {
                    hoverTimer += Time.deltaTime;
                    if (hoverTimer >= hoverDuration)
                    {
                        button.onClick.Invoke();
                        hoverTimer = 0f; // Reset the timer after clicking
                    }
                }
                else
                {
                    hoveredButton = button;
                    hoverTimer = 0f;
                }
                return;
            }
        }

        // Reset if no button is hovered
        hoveredButton = null;
        hoverTimer = 0f;
    }
}
