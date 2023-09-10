from .aws import AmazonCloud
from .google import GoogleCloud

clouds = {"google": GoogleCloud, "aws": AmazonCloud}
cloud_names = list(clouds)
