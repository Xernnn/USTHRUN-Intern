using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Fruits : MonoBehaviour
{
    public GameObject slicedFruit;
    public GameObject fruitJuice;
    void Start()
    {
        
    }

    void Update()
    {
        
    }

    private void InstantiateSlicedFruit()
    {
        GameObject instantiatedFruit = Instantiate(slicedFruit, transform.position, transform.rotation);
        GameObject instantiatedJuice = Instantiate(fruitJuice, new Vector3(transform.position.x, transform.position.y, 0), fruitJuice.transform.rotation);
    
        Rigidbody[] slicedRb = instantiatedFruit.transform.GetComponentsInChildren<Rigidbody>();

        foreach (Rigidbody srb in slicedRb)
        {
            srb.AddExplosionForce(130f, transform.position, 10);
        }

        Destroy(instantiatedFruit, 4);
        Destroy(instantiatedJuice, 4);
    }

    private void OnMouseDown()
    {
        InstantiateSlicedFruit();
        Destroy(gameObject);
    }
}
