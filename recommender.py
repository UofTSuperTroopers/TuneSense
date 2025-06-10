import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, sum as _sum, count, mean, coalesce
from pyspark.ml.recommendation import ALS
from pyspark.sql.types import IntegerType, StructType, StructField, StringType
import random

class RunRecommender:
	def __init__(self):
		self.spark = SparkSession.builder.appName("TuneSenseRecommender").getOrCreate()

	def main(self):
		# Load data
		rawUserArtistData = self.spark.read.text("data/user_artist_data.txt").rdd.map(lambda r: r[0])
		rawArtistData = self.spark.read.text("data/artist_data.txt").rdd.map(lambda r: r[0])
		rawArtistAlias = self.spark.read.text("data/artist_alias.txt").rdd.map(lambda r: r[0])

		bArtistAlias = self.spark.sparkContext.broadcast(self.buildArtistAlias(rawArtistAlias))
		allData = self.buildCounts(rawUserArtistData, bArtistAlias).cache()

		als = ALS(
			maxIter=5,
			regParam=0.01,
			userCol="user",
			itemCol="artist",
			ratingCol="count",
			coldStartStrategy="drop",
			nonnegative=True
		)
		model = als.fit(allData)
		allData.unpersist()

		userID = 2093760
		topRecommendations = self.makeRecommendations(model, userID, 5)

		recommendedArtistIDs = [row['artist'] for row in topRecommendations.select("artist").collect()]
		artistByID = self.buildArtistByID(rawArtistData)
		artistByID_df = self.spark.createDataFrame(artistByID, ["id", "name"])
		recommended_df = self.spark.createDataFrame([(i,) for i in recommendedArtistIDs], ["id"])
		artistByID_df.join(recommended_df, "id").select("name").show()

		model.userFactors.unpersist()
		model.itemFactors.unpersist()

	def buildArtistByID(self, rawArtistData):
		result = []
		for line in rawArtistData.collect():
			parts = line.split('\t', 1)
			if len(parts) != 2:
				continue
			try:
				id = int(parts[0])
				name = parts[1].strip()
				if name:
					result.append((id, name))
			except ValueError:
				continue
		return result

	def buildArtistAlias(self, rawArtistAlias):
		alias = {}
		for line in rawArtistAlias.collect():
			parts = line.strip().split('\t')
			if len(parts) != 2:
				continue
			try:
				artist = int(parts[0])
				alias_id = int(parts[1])
				alias[artist] = alias_id
			except ValueError:
				continue
		return alias

	def buildCounts(self, rawUserArtistData, bArtistAlias):
		def parse(line):
			try:
				userID, artistID, count = map(int, line.strip().split())
				finalArtistID = bArtistAlias.value.get(artistID, artistID)
				return (userID, finalArtistID, count)
			except Exception:
				return None
		schema = StructType([
			StructField("user", IntegerType(), True),
			StructField("artist", IntegerType(), True),
			StructField("count", IntegerType(), True)
		])
		parsed = rawUserArtistData.map(parse).filter(lambda x: x is not None)
		return self.spark.createDataFrame(parsed, schema)

	def makeRecommendations(self, model, userID, howMany):
		from pyspark.sql import Row
		user_df = self.spark.createDataFrame([Row(user=userID)])
		user_artists = model.recommendForUserSubset(user_df, howMany)
		# Flatten recommendations
		def extract_recs(row):
			user = row['user']
			for rec in row['recommendations']:
				yield (user, rec['artist'], rec['rating'])
		recs = user_artists.rdd.flatMap(extract_recs)
		schema = StructType([
			StructField("user", IntegerType(), True),
			StructField("artist", IntegerType(), True),
			StructField("prediction", IntegerType(), True)
		])
		return self.spark.createDataFrame(recs, schema)

# Entry point
if __name__ == '__main__':
	app = RunRecommender()
	app.main()

