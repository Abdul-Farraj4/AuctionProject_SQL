/** **
* ITCS 3160-0002, Spring 2024
* Marco Vieira, marco.vieira@charlotte.edu
* University of North Carolina at Charlotte

* IMPORTANT: this file includes the Python implementation of the REST API
* It is in this file that yiu should implement the functionalities/transactions   
*/
package edu.charlotte.cs.itcs3160;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class DemoProj {

    public enum StatusCode {

        SUCCESS ("success", 200),
        API_ERROR ("api_error", 400),
        INTERNAL_ERROR ("internal_error", 500);
    
        private final String description; 
        private final int code; 
        
        private StatusCode(String description, int code) {
            this.description = description;
            this.code = code;
        }
        
        public String description() { 
            return description; 
        }

        public int code() { 
            return code; 
        }
    }


    private static final Logger logger = LoggerFactory.getLogger(DemoProj.class);

    @GetMapping("/")
    public String landing() {
        return "Hello World (Java)!  <br/>\n"
                + "<br/>\n"
                + "Check the sources for instructions on how to use the endpoints!<br/>\n"
                + "<br/>\n"
                + "ITCS 3160-002, Spring 2024<br/>\n"
                + "<br/>";
    }

    /**
     * Demo GET
     *
     *
     * Obtain all users, in JSON format
     *
     * To use it, access: <br>
     * http://localhost:8080/users/
     *
     *
     * @return
     */
    @GetMapping(value = "/users/", produces = "application/json")
    @ResponseBody
    public Map<String, Object> getAllUsers() {
        logger.info("###              DEMO: GET /users              ###");
        Connection conn = RestServiceApplication.getConnection();
        Map<String, Object> returnData = new HashMap<String, Object>();
        List<Map<String, Object>> results = new ArrayList<>();

        try (Statement stmt = conn.createStatement()) {
            ResultSet rows = stmt.executeQuery("SELECT username, name, city FROM users");
            logger.debug("---- users  ----");
            while (rows.next()) {
                Map<String, Object> content = new HashMap<>();
                logger.debug("'username': {}, 'name': {}, 'city': {}",
                        rows.getString("username"), rows.getString("name"), rows.getString("city")
                );
                content.put("username", rows.getString("username"));
                content.put("name", rows.getString("name"));
                content.put("city", rows.getString("city"));
                results.add(content);
            }

            returnData.put("status", StatusCode.SUCCESS.code());
            returnData.put("results", results);

        } catch (SQLException ex) {
            logger.error("Error in DB", ex);
            returnData.put("status", StatusCode.INTERNAL_ERROR.code());
            returnData.put("errors", ex.getMessage());
        }
        return returnData;
    }

    /**
     * Demo GET
     *
     *
     * Obtain user with {@code username}
     *
     * To use it, access: <br>
     * http://localhost:8080/users/ssmith
     *
     *
     * @param username id of the user to be selected
     * @return data of the user
     */
    @GetMapping(value = "/users/{username}", produces = "application/json")
    @ResponseBody
    public Map<String, Object> getuser(
            @PathVariable("username") String username
    ) {
        logger.info("###              DEMO: GET /users              ###");
        Connection conn = RestServiceApplication.getConnection();

        Map<String, Object> returnData = new HashMap<String, Object>();

        Map<String, Object> content = new HashMap<>();
        try (PreparedStatement ps = conn.prepareStatement("SELECT username, name, city FROM users WHERE username = ?")) {
            ps.setString(1, username);
            ResultSet rows = ps.executeQuery();
            logger.debug("---- selected user  ----");
            if (rows.next()) {
                logger.debug("'username': {}, 'name': {}, 'city': {}", rows.getString("username"), rows.getString("name"), rows.getString("city"));
                content.put("username", rows.getString("username"));
                content.put("name", rows.getString("name"));
                content.put("city", rows.getString("city"));
            }

            returnData.put("status", StatusCode.SUCCESS.code());
            returnData.put("results", content);

        } catch (SQLException ex) {
            logger.error("Error in DB", ex);
            returnData.put("status", StatusCode.INTERNAL_ERROR.code());
            returnData.put("errors", ex.getMessage());
        }
        return returnData;
    }

    /**
     * Demo POST
     *
     *
     * Add a new user in a JSON payload
     *
     * To use it, you need to use postman or curl:
     *
     * {@code curl -X POST http://localhost:8080/users/ -H "Content-Type: application/json" -d
     * '{"city": "London", "username": "ppopov", "name": "Peter Popov"}'
     *
     *
     */
    @PostMapping(value = "/users/", consumes = "application/json")
    @ResponseBody
    public Map<String, Object> createuser(
            @RequestBody Map<String, Object> payload
    ) {

        logger.info("###              DEMO: POST /users              ###");
        Connection conn = RestServiceApplication.getConnection();

        logger.debug("---- new user  ----");
        logger.debug("payload: {}", payload);

        Map<String, Object> returnData = new HashMap<String, Object>();

        // validate all the required inputs and types, e.g.,
        if (!payload.containsKey("city")) {
            logger.warn("city are required to update");
            returnData.put("status", StatusCode.API_ERROR.code());
            returnData.put("errors", "city are required to update");
            return returnData;
        }

        try (PreparedStatement ps = conn.prepareStatement(""
                + "INSERT INTO users (username, name, city) "
                + "         VALUES (  ? ,   ? ,    ? )")) {
            ps.setString(1, (String) payload.get("username"));
            ps.setString(2, (String) payload.get("name"));
            ps.setString(3, (String) payload.get("city"));
            int affectedRows = ps.executeUpdate();
            conn.commit();

            returnData.put("status", StatusCode.SUCCESS.code());
            returnData.put("results", "user inserted successfully");

        } catch (SQLException ex) {
            logger.error("Error in DB", ex);
            try {
                conn.rollback();
            } catch (SQLException ex1) {
                logger.warn("Couldn't rollback", ex);
            }

            returnData.put("status", StatusCode.INTERNAL_ERROR.code());
            returnData.put("errors", ex.getMessage());

        } finally {
            try {
                conn.close();
            } catch (SQLException ex) {
                logger.error("Error in DB", ex);
            }
        }
        return returnData;
    }

    /**
     * Demo PUT
     *
     *
     * Update a user based on the a JSON payload
     *
     * o use it, you need to use postman or curl:
     *
     * {@code curl -X PUT http://localhost:8080/users/ -H "Content-Type: application/json" -d '{"city": "Raleigh"}'
     *
     */
    @PutMapping(value = "/users/{username}", consumes = "application/json")
    @ResponseBody
    public Map<String, Object> updateuser(
            @PathVariable("username") String username,
            @RequestBody Map<String, Object> payload
    ) {

        logger.info("###              DEMO: PUT /users               ###");

        Map<String, Object> returnData = new HashMap<String, Object>();

        // validate all the required inputs and types, e.g.,
        if (!payload.containsKey("city")) {
            logger.warn("city are required to update");
            returnData.put("status", StatusCode.API_ERROR.code());
            returnData.put("errors", "city are required to update");
            return returnData;
        }

        logger.info("---- update user  ----");
        logger.debug("content: {}", payload);
        Connection conn = RestServiceApplication.getConnection();

        try (PreparedStatement ps = conn.prepareStatement(""
                + "UPDATE users"
                + "   SET city = ? "
                + " WHERE username = ?")) {

            ps.setString(1, (String) payload.get("city"));
            ps.setString(2, username);

            int affectedRows = ps.executeUpdate();
            conn.commit();

            returnData.put("status", StatusCode.SUCCESS.code());
            returnData.put("results", "user updated successfully");

        } catch (SQLException ex) {
            logger.error("Error in DB", ex);
            try {
                conn.rollback();
            } catch (SQLException ex1) {
                logger.warn("Couldn't rollback", ex);
            }

            returnData.put("status", StatusCode.INTERNAL_ERROR.code());
            returnData.put("errors", ex.getMessage());
        } finally {
            try {
                conn.close();
            } catch (SQLException ex) {
                logger.error("Error in DB", ex);
            }
        }
        return returnData;
    }
}
