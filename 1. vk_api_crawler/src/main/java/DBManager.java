import java.io.*;
import java.sql.*;
import java.util.*;

public class DBManager {

    public Connection getConnection() {
        Connection connection = null;
        Properties properties = new Properties();
        try {
            properties.load(getClass().getResourceAsStream("config.properties"));
        } catch (IOException e) {
            e.printStackTrace();
        }
        try {
            connection = DriverManager.getConnection(
                properties.getProperty("db.host"), properties.getProperty("db.login"), "");
        } catch (SQLException throwables) {
            throwables.printStackTrace();
        }
        return connection;
    }

    public void addWord(Connection connection, String word, int count) {
        String SQL_ADD_WORD = "insert into words values ( '" + word + "', " + count + ");";
        try {
            Statement st = connection.createStatement();
            st.executeUpdate(SQL_ADD_WORD);
        } catch (SQLException throwables) {
            throwables.printStackTrace();
        }
    }

    public void removePreviouseResult(Connection connection) {
        String SQL_DELETE_ALL_STRINGS = "DELETE FROM words";
        try {
            Statement st = connection.createStatement();
            st.executeUpdate(SQL_DELETE_ALL_STRINGS);
        } catch (SQLException throwables) {
            throwables.printStackTrace();
        }
    }
}
