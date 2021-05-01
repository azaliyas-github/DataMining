import lombok.*;

import java.io.*;
import java.lang.reflect.*;
import java.nio.file.*;
import java.util.*;

public class Main {

    public static void main(String[] args) throws IOException {
        Random random = new Random();
        int arrayLength = 1000000;

        // это массивы переменных
        ArrayPointer[] oneHundredPointers = new ArrayPointer[100];
        ArrayPointer[] fiveHundredPointers = new ArrayPointer[500];

        // указываем для каждой переменной рандомный начальный индекс
        for (int i = 0; i < 100; ++i) {
            oneHundredPointers[i] = new ArrayPointer(random.nextInt(arrayLength));
        }
        for (int i = 0; i < 500; ++i) {
            fiveHundredPointers[i] = new ArrayPointer(random.nextInt(arrayLength));
        }

        // в потоке создаем таблицу(hashmap) для подсчета 0го и 1го моментов
        // и перерасчитываем значения некоторых полей переменных
        HashMap<Integer, Integer> elementsCounts = new HashMap<>();
        try (PrintWriter printWriter = new PrintWriter("result.txt")) {
            printWriter.print("stream: ");
            for (int i = 0; i < arrayLength; i++) {
                int element = random.nextInt(1000);

                printWriter.print(element);
                if (i != arrayLength - 1)
                    printWriter.print(" ");
                if (i % 30 == 29)
                    printWriter.println();

                processNextElement(elementsCounts, element);

                for (ArrayPointer pointer : oneHundredPointers)
                    pointer.processNextElement(element);
                for (ArrayPointer pointer : fiveHundredPointers)
                    pointer.processNextElement(element);
            }
            printWriter.println();
            printWriter.print("zero moment: ");
            printWriter.println(zeroMoment(elementsCounts));

            printWriter.print("first moment: ");
            printWriter.println(firstMoment(elementsCounts));

            printWriter.print("second moment for 100 variables: ");
            printWriter.println(secondMoment(arrayLength, oneHundredPointers));

            printWriter.print("second moment for 500 variables: ");
            printWriter.println(secondMoment(arrayLength, fiveHundredPointers));
        }
    }

    static void processNextElement(HashMap<Integer, Integer> elementsCounts, int element) {
        int elementCount = elementsCounts.getOrDefault(element, 0);
        elementsCounts.put(element, elementCount + 1);
    }

    static int zeroMoment(HashMap<Integer, Integer> hashMap) {
        return hashMap.size();
    }

    static int firstMoment(HashMap<Integer, Integer> hashMap) {
        int moment = 0;
        for (Integer value : hashMap.values()) {
            moment = moment + value;
        }
        return moment;
    }

    static int secondMoment(int streamLength, ArrayPointer[] array) {
        int elementCountSum = 0;
        for (ArrayPointer arrayPointer : array) {
            elementCountSum = elementCountSum + arrayPointer.getElementCount();
        }

        return (int)((long)streamLength * (2 * elementCountSum - array.length) / array.length);
    }

    private static class ArrayPointer {
        private final int startIndex;
        private int currentIndex;
        private int elementValue;
        private int elementCount;

        public ArrayPointer(int startIndex) {
            this.startIndex = startIndex;
            this.currentIndex = -1;
            elementCount = 0;
        }

        public int getElementCount() {
            return elementCount;
        }

        public void processNextElement(int elementValue) {
            ++currentIndex;
            if (currentIndex < startIndex)
                return;

            if (currentIndex == startIndex)
                this.elementValue = elementValue;

            if (elementValue == this.elementValue)
                ++elementCount;
        }
    }
}
