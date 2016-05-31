import org.apache.spark.ml.classification.LogisticRegression
import org.apache.spark.ml.feature.VectorAssembler

val va = new VectorAssembler().setInputCols(Array("_c0", "_c1", "_c2")).setOutputCol("features")
val df = va.transform(spark.read.format("csv").option("inferSchema", "true").load(path))

