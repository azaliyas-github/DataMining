import com.jayway.jsonpath.*;
import net.minidev.json.*;

import java.io.*;
import java.net.*;
import java.sql.*;
import java.util.*;

public class Main {
    private String URL = "https://api.vk.com/method/wall.get?domain=itis_kfu&count=3&filter=owner&access_token=842200bf842200bf842200bf6b84549cb688422842200bfe415fea1014aa666102d77fc&v=5.130";
    private String access_token;
    private String domain = "itis_kfu";
    private String count = "200";

    public static void main(String[] args) throws IOException {
        // Добавить в метод downloadPosts() параметры строки
        String[] texts1 = downloadPosts(0);
        String[] texts2 = downloadPosts(100);

        StringBuilder sbTexts = new StringBuilder();
        for (String s : texts1) {
            sbTexts.append(s).append(" ");
        }
        for (String s : texts2) {
            sbTexts.append(s).append(" ");
        }

        String unitedString = sbTexts.toString();
        unitedString =  Parser.removeUrls(unitedString);
        unitedString = Parser.removeOddSymbols(unitedString);
        //System.out.println(unitedString);
        HashMap<String, Integer> allUniqueWords = Parser.returnAllUniqueWords(unitedString);
        save(new DBManager(), allUniqueWords);
    }

    private static String[] downloadPosts(int offset) {
        String accessToken = null; // получить из настроек, например, settings.get("access_token");
        String URL = "https://api.vk.com/method/wall.get?domain=itis_kfu&offset=" + offset +
                "&count=100&filter=owner&access_token=842200bf842200bf842200bf6b84549cb688422842200bfe415fea1014aa666102d77fc&v=5.130";
        String line = "";
        try {
            URL url2 = new URL(URL);
            BufferedReader reader = new BufferedReader(new InputStreamReader(url2.openStream()));
            line = reader.readLine();
            reader.close();

        } catch (IOException e) {
            // ...
        }

        JSONArray jsonArray = JsonPath.read(line, "$.response.items[*].text");
        Object[] textsAsObjects = jsonArray.toArray();
        String[] texts = new String[textsAsObjects.length];

        for (int i = 0; i < texts.length; i++) {
            texts[i] = (String) textsAsObjects[i];
        }
        return texts;
    }

    private static void save(DBManager dbManager, HashMap<String, Integer> words) {
        Set<Map.Entry<String, Integer>> wordsSet = words.entrySet();
        Connection connection = dbManager.getConnection();
        dbManager.removePreviouseResult(connection);
        for (Map.Entry<String, Integer> wordMap : wordsSet) {
            dbManager.addWord(connection, wordMap.getKey(), wordMap.getValue());
        }
        try {
            connection.close();
        } catch (SQLException throwables) {
            throwables.printStackTrace();
        }
    }
}
