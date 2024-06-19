using UnityEngine;
using System;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Threading;

public class UDPReceive : MonoBehaviour
{
    Thread receiveThread;
    UdpClient client;
    public int port = 3285;
    public bool startReceiving = true;
    public bool printToConsole = true; // Set to true to print received data
    public string data;

    public void Start()
    {
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();
        Debug.Log("UDPReceive started on port " + port);
    }

    private void ReceiveData()
    {
        client = new UdpClient(port);
        while (startReceiving)
        {
            try
            {
                IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, 0);
                byte[] dataByte = client.Receive(ref anyIP);
                data = Encoding.UTF8.GetString(dataByte);

                if (printToConsole)
                {
                    Debug.Log("Received data: " + data);
                }

                // Process the received data
                string[] coordinates = data.Split(',');
                if (coordinates.Length == 2)
                {
                    int centerX = int.Parse(coordinates[0]);
                    int centerY = int.Parse(coordinates[1]);

                    // Use the received coordinates in Unity
                    Debug.Log($"Received center coordinates: ({centerX}, {centerY})");
                }
            }
            catch (Exception err)
            {
                Debug.LogError("Error receiving data: " + err.ToString());
            }
        }
    }
}
