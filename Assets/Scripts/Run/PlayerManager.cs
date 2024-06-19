using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class PlayerManager : MonoBehaviour
{
    public static bool gameOver;
    public GameObject gameOverPanel;

    public static bool isGameStarted;

    public static float point;
    public Text pointText;

    private PlayerController playerController;

    void Start()
    {
        gameOver = false;
        isGameStarted = false;
        Time.timeScale = 1.0f;
        point = 0;
        playerController = FindObjectOfType<PlayerController>();

        if (playerController == null)
        {
            Debug.LogError("PlayerController not found!");
        }
    }

    void Update()
    {
        if (gameOver)
        {
            Time.timeScale = 0;
            gameOverPanel.SetActive(true);
            StartCoroutine(EndGame(2f));
        }

        if (Input.GetKeyDown(KeyCode.Space) && !isGameStarted)
        {
            isGameStarted = true;
        }

        if (playerController != null && isGameStarted)
        {
            point = playerController.transform.position.z;
            pointText.text = point.ToString("F2");
        }
    }

    IEnumerator EndGame(float delay)
    {
        yield return new WaitForSeconds(delay);
        gameOverPanel.SetActive(true);
    }
}
