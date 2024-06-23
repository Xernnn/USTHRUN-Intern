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
    public Text GameOverPointText;

    private PlayerController playerController;
    private Vector3 startPosition;

    public static int numberOfCoins;
    public Text coinsText;
    public Text highscoreText;
    private int highscore;

    void Start()
    {
        gameOver = false;
        isGameStarted = false;
        Time.timeScale = 1.0f;

        point = 0;
        pointText.text = "Score: " + point;

        // Load saved coins and high score
        numberOfCoins = PlayerPrefs.GetInt("Coins", 0);
        coinsText.text = "Coins: " + numberOfCoins;

        highscore = PlayerPrefs.GetInt("Highscore", 0);
        highscoreText.text = "Highscore: " + highscore;

        playerController = FindObjectOfType<PlayerController>();
        startPosition = playerController.transform.position;
    }

    void Update()
    {
        if (gameOver)
        {
            StartCoroutine(EndGame(2f));
        }

        if (Input.GetKeyDown(KeyCode.Space) && !isGameStarted)
        {
            isGameStarted = true;
        }

        if (isGameStarted && !gameOver)
        {
            UpdateScore();
        }

        coinsText.text = "Coins: " + numberOfCoins;
    }

    void UpdateScore()
    {
        float distance = Vector3.Distance(startPosition, playerController.transform.position);
        point = distance;
        pointText.text = "Score: " + Mathf.Floor(point);
    }

    IEnumerator EndGame(float delay)
    {
        yield return new WaitForSeconds(delay);
        GameOverPointText.text = "SCORE: " + Mathf.FloorToInt(point);
        
        // Save the number of coins
        PlayerPrefs.SetInt("Coins", numberOfCoins);

        // Check if the current score is higher than the highscore
        if (Mathf.FloorToInt(point) > highscore)
        {
            highscore = Mathf.FloorToInt(point);
            PlayerPrefs.SetInt("Highscore", highscore);
            highscoreText.text = "Highscore: " + highscore;
        }

        gameOverPanel.SetActive(true);
        Time.timeScale = 0;
    }
}