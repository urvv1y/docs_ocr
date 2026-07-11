package com.project.ocr;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class OcrApp {
    public static void main(String[] args) {
        SpringApplication.run(OcrApp.class, args);
    }
}

// http://localhost:8080/api/receipts
// http://localhost:8080/h2-console
// http://localhost:8080/api/upload

