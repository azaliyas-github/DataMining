import java.io.*;
import java.nio.file.*;
import java.util.*;

public class Main {

    public static void main(String[] args) throws IOException {
        List<String> list = Files.readAllLines(Paths.get("texts/0.txt"));
        CountableBloomFilter countableBloomFilter =
                new CountableBloomFilter(0.0001, list.size());

        for (String word : list)
            countableBloomFilter.add(word);

        for (String word : list)
            assert(countableBloomFilter.contains(word));

        String[] nonPresentWords = {
                "123456", "qwerty", "TROLLFAKE", "OLOLo", "oewlvsjbnjdsbn",
                "qazxswedcvfrertg", "><", "", "Habrahabr", "2ch"};
        for (String word : nonPresentWords)
            System.out.println(word + ": " + countableBloomFilter.contains(word));
    }
}
