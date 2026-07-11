package com.project.ocr;

import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClient;
import org.springframework.web.multipart.MultipartFile;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.ObjectMapper;

/**
 * @author urvv1y
 * REST controller, creates the endpoint
 */
@RestController
@RequestMapping("/api")
public class OrcControll {
    private final RestClient restClient;
    private final ReceiptRepository receiptRepository;
    private final ObjectMapper objectMapper;

    public OrcControll(ReceiptRepository receiptRepository) {
        this.restClient = RestClient.create("http://localhost:8000");
        this.receiptRepository = receiptRepository;
        this.objectMapper = new ObjectMapper();
    }

    @PostMapping("/upload")
    public ResponseEntity<String> uploadImage(@RequestParam("file") MultipartFile file,  @RequestParam(value = "lang", defaultValue = "ces") String lang) {
        try {
            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("file", file.getResource());
            body.add("lang", lang);

            String response = restClient.post()
                    .uri("/extract")
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(body)
                    .retrieve()
                    .body(String.class);
            JsonNode root = objectMapper.readTree(response);
            JsonNode dataNode = root.path("data");

            String store = dataNode.hasNonNull("Provozovatel") ? dataNode.get("Provozovatel").asString() : dataNode.path("Merchant").asString(null);
            String date = dataNode.hasNonNull("Datum") ? dataNode.get("Datum").asString() : dataNode.path("Date").asString(null);
            String payment = dataNode.hasNonNull("Platba")? dataNode.get("Platba").asString() : dataNode.path("Total").asString(null);
            String total = dataNode.hasNonNull("Celkem") ? dataNode.get("Celkem").asString() : dataNode.path("Total").asString(null);

            Receipt receipt = new Receipt(store, date, payment, total);
            receiptRepository.save(receipt);

            return ResponseEntity.ok("Document read successfully - doc_id: " + receipt.getId());
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(e.getMessage());
        }
    }

}
