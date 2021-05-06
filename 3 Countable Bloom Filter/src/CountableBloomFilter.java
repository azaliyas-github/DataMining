import java.util.*;

public class CountableBloomFilter {
    private final int capacity;
    private final int[] bloomFilterArray;
    private final ArrayList<HashFunction<String>> hashFunctions;

    private int objectsCount = 0;

    CountableBloomFilter(double falsePositiveRate, int capacity) {
        this.capacity = capacity;

        // m = -n * ln(eps) / (ln(2))^2
        double log2 = Math.log(2);
        double falsePositiveRateLog = Math.log(falsePositiveRate);
        int arrayLength = (int)Math.ceil(-capacity * falsePositiveRateLog / (log2 * log2));
        bloomFilterArray = new int[arrayLength];

        // k = -ln(eps) / ln(2)
        int hashFunctionsCount = (int)Math.ceil(-falsePositiveRateLog / log2);
        hashFunctions = generateHashFunctions(hashFunctionsCount);
    }

    public void add(String element) {
        if (objectsCount == capacity)
            throw new IllegalStateException(
                    "Превышен предел количества объектов в " + capacity + "элементов в фильтре Блума");
        for (var hashFunction : hashFunctions) {
            var hash = hashFunction.calculateHash(element);
            int elementNumber = Math.abs(hash) % bloomFilterArray.length;
            ++bloomFilterArray[elementNumber];
        }
        objectsCount++;
    }

    public void remove(String element) {
        for (var hashFunction : hashFunctions) {
            var hash = hashFunction.calculateHash(element);
            int elementNumber = Math.abs(hash) % bloomFilterArray.length;

            if (bloomFilterArray[elementNumber] == 0)
                throw new IllegalArgumentException("Элемента \"" + element + "\" нет в фильтре Блума");
            --bloomFilterArray[elementNumber];
        }
        objectsCount--;
    }

    public boolean contains(String element) {
        for (var hashFunction : hashFunctions) {
            var hash = hashFunction.calculateHash(element);
            int elementNumber = Math.abs(hash) % bloomFilterArray.length;
            if (bloomFilterArray[elementNumber] == 0) {
                return false;
            }
        }
        return true;
    }

    private ArrayList<HashFunction<String>> generateHashFunctions(int hashFunctionsCount) {
        var functions = new ArrayList<HashFunction<String>>();

        for (int i = 0; i < hashFunctionsCount; i++) {
            var seed = (int)Math.floor(Math.random() * 37) + 19;
            functions.add(
                object ->
                {
                    var hash = 1;
                    for (var charIndex = 0; charIndex < object.length(); ++charIndex)
                        hash = seed * hash + object.charAt(charIndex);
                    return hash;
                });
        }

        return functions;
    }
}
