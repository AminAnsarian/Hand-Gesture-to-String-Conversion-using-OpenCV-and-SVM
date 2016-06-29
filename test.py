import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
import pylab as pl
import random
from sklearn import ensemble
from PIL import Image
import numpy as np
import cv2


digits = load_digits()
img = Image.open('ts.jpg')
img_gray = img.convert('L')
# # img2 = cv2.imread('ts.jpg')
# img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


temp_digit = Image.fromarray(digits.images[0])

width, height = temp_digit.size

img_gray.thumbnail((width, height), Image.ANTIALIAS)
img_array = np.array(img_gray)

print(img_gray)

n_samples = len(digits.images)
x = digits.images.reshape((n_samples, -1))
img_array_1 = img_array.reshape((1, -1))
y = digits.target

sample_index = random.sample(range(len(x)), len(x) // 5) #20-80
valid_index = [i for i in range(len(x)) if i not in sample_index]

sample_images = [x[i] for i in sample_index]
valid_images = [x[i] for i in valid_index]

sample_target = [y[i] for i in sample_index]
valid_target = [y[i] for i in valid_index]

classifier = ensemble.RandomForestClassifier()

classifier.fit(sample_images, sample_target)

score = classifier.score(valid_images, valid_target)
print('Random Tree Classifier:\n')
print('Score\t'+str(score))

i = 150

pl.gray()
pl.matshow(img_array)
pl.show()
print(classifier.predict(img_array))