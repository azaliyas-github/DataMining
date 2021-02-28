import com.jayway.jsonpath.*;
import net.minidev.json.*;

import java.io.*;
import java.net.*;

public class Main {
    private String URL = "https://api.vk.com/method/wall.get?domain=itis_kfu&count=3&filter=owner&access_token=842200bf842200bf842200bf6b84549cb688422842200bfe415fea1014aa666102d77fc&v=5.130";
    private String access_token;
    private String domain = "itis_kfu";
    private String count = "200";

    public static void main(String[] args) throws IOException {
        // Добавить в метод downloadPosts() параметры строки
        String[] texts = downloadPosts();


        for (int i = 0; i < texts.length; i++) {
            texts[i] = Parser.removeUrls(texts[i]);
            texts[i] = Parser.removeOddSymbols(texts[i]);

            Parser.returnAllUniqueWords(texts[i]);
        }
    }

    private static String[] downloadPosts() {
        String accessToken = null; // получить из настроек, например, settings.get("access_token");
        String URL = "https://api.vk.com/method/wall.get?domain=itis_kfu&count=200&filter=owner&access_token=842200bf842200bf842200bf6b84549cb688422842200bfe415fea1014aa666102d77fc&v=5.130";
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
}
