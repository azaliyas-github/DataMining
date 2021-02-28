import emoji4j.*;

import java.util.*;

public class Parser {

    public static HashMap<String, Integer> returnAllUniqueWords(String posts) {
        HashMap<String, Integer> allUniqueWords = new HashMap<>();
        String[] wordsList = posts.split(" ");

        for (String word : wordsList) {
            if (allUniqueWords.containsKey(word)) {
                allUniqueWords.put(word, allUniqueWords.get(word) + 1);
            }
            else {
                allUniqueWords.put(word, 1);
            }
        }
        return allUniqueWords;
    }

    public static String removeOddSymbols(String post) {
        post = EmojiUtils.removeAllEmojis(post);
        // Одновременно удаляю два эмодзи
        post = post.replaceAll("[✒\uD83C\uDFDB\uD83C\uDFFB\u200D♂\uD83D\uDCFD⛹\uD83C\uDFFC]+"," ");
        post = post.replaceAll("[\\p{Punct}«»—–“”]+", " ");
//        post = post.replaceAll("[^\\w\\d\\s]+", " ");
        post = post.replaceAll("[\\s ]+", " ");
        return post.strip();
    }

    public static String removeUrls(String text) {
       final String URL_REGEX = "((https?|ftp)://|(www|ftp)\\.)?[a-z0-9-]+(\\.[a-z0-9-]+)+([/?].*)?";

       return text.replaceAll(URL_REGEX, "");
    }

    // избавить текст от эмодзи (массив исходного текста -> такой же массив без эмодзи)
    // избавить текст от ссылок (массив исходного текста -> такой же массив без эмодзи)
    // найти уникальные слова (массив исходного текста -> массив из уникальных слов)
}
