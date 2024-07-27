### **Understanding '''learn_one'''**

In online (or incremental) machine learning, models learn from one sample at a time, allowing them to update their parameters incrementally as new data arrives. This is different from batch learning, where models are trained on a whole dataset at once.

The learn_one method is used to update the model with a single observation (a single instance of features and its corresponding target value).

* Steps Involved in _**learn_one --> content-based / linear regression**_

#### **Prediction (Before Update):**

The model predicts the target value using the current weights and the provided features.
Let's denote this prediction as **^𝑦**


#### **Error Calculation:**

The model calculates the error (difference) between the predicted value **^𝑦**
and the actual target value 
𝑦 (i.e., liked). 

`error = 𝑦 − ^𝑦`

**Gradient Calculation:**

The model calculates the gradient of the error with respect to the model parameters (weights). This involves computing the partial derivatives of the error with respect to each weight.

**Weights Update:**

The model updates its weights to minimize the error. This is done using a learning rate (step size) and the computed gradients.

`𝑤𝑖 ← 𝑤𝑖+ learning rate × error × 𝑥𝑖`

𝑥𝑖 = features, 𝑤𝑖 = weight


* Steps Involved in **_learn_one -- Collaboration filtration_**

 **Retrieve Latent Factors:**
The model retrieves the current latent factors for the given user and item.
If the user or item is new, it initializes their latent factors.

**Predict the Current Interaction:** The model computes the predicted interaction (rating) as the dot product of the user’s and item’s latent factors:
`^𝑦 = 𝑢𝑖 ⋅ 𝑣𝑗`

**Calculate the Error:**

The error 𝑒 is the difference between the actual interaction 𝑦 (in this case, liked) and the predicted interaction 
`error = 𝑦 − ^𝑦`

**Update Latent Factors:** The model updates the latent factors using gradient descent to minimize the prediction error. For each latent factor 

![img_1.png](img_1.png)


## Binary Features

Representation of Presence/Absence:

Binary Features: Using binary values (0 or 1) to represent features is a common practice in recommendation systems and machine learning models, especially when the features indicate the presence or absence of certain attributes. 

In this case:
user_interest_sports = 1 indicates that the user is interested in sports.
video_topic_fitness = 1 indicates that the video is about fitness.
0 and 1 Values: If a user is not interested in sports, the value would be 0. Similarly, if a video is not about fitness, the value would be 0.

**The target value (liked)** provides feedback to the model.
If the model's prediction was incorrect (i.e., predicted the user wouldn't like the video, but they did), the model adjusts its weights to improve future predictions.



## StandardScaler in Online Learning

In online learning, StandardScaler is used to normalize the features incrementally as new data arrives. This normalization process helps in bringing all the features to the same scale, which is important for models like linear regression to perform well.

#### Steps Involved:

Learning from Features (scaler.learn_one(features)):

The learn_one method updates the internal state of the scaler with the new data. It calculates and maintains the mean and variance of each feature incrementally. This step ensures that the scaler keeps track of the necessary statistics to standardize the features over time.

