package com.project.ocr;

import jakarta.persistence.criteria.CriteriaBuilder;
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
import org.springframework.web.bind.annotation.GetMapping;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * @author urvv1y
 * REST controller, creates the endpoint
 */
@RestController
@RequestMapping("/api")
public class OrcControll {
    private final RestClient restClient;
    private final ReceiptRepository receiptRepository;
    private final InvoiceRepository invoiceRepository;
    private final ObjectMapper objectMapper;

    public OrcControll(ReceiptRepository receiptRepository, InvoiceRepository invoiceRepository) {
        this.restClient = RestClient.create("http://ocr-python:8000");
        this.receiptRepository = receiptRepository;
        this.invoiceRepository = invoiceRepository;
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
            String payment = dataNode.hasNonNull("Platba")? dataNode.get("Platba").asString() : dataNode.path("Payment").asString(null);
            String total = dataNode.hasNonNull("Celkem") ? dataNode.get("Celkem").asString() : dataNode.path("Total").asString(null);

            Receipt receipt = new Receipt(store, date, payment, total);
            receiptRepository.save(receipt);

            return ResponseEntity.ok("Document read successfully - doc_id: " + receipt.getId());
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(e.getMessage());
        }

    }

    @PostMapping("/upload-invoice")
    public ResponseEntity<String> uploadInvoiceImage(@RequestParam("file") MultipartFile file, @RequestParam(value = "lang", defaultValue = "ces") String lang) {
        try {
            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("file", file.getResource());
            body.add("lang", lang);

            String response = restClient.post()
                    .uri(uriBuilder -> uriBuilder.path("/extract").queryParam("lang", lang).build())
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(body)
                    .retrieve()
                    .body(String.class);
            JsonNode root = objectMapper.readTree(response);
            JsonNode dataNode = root.path("data");


            String seller = dataNode.hasNonNull("Provozovatel") ? dataNode.get("Provozovatel").asString() : dataNode.path("Merchant").asString(null);
            String invoiceDate = dataNode.hasNonNull("Datum") ? dataNode.get("Datum").asString() : dataNode.path("Date").asString(null);
            String paymentMethod = dataNode.hasNonNull("Platba") ? dataNode.get("Platba").asString() : dataNode.path("Payment").asString(null);
            String totalPrice = dataNode.hasNonNull("Celkem") ? dataNode.get("Celkem").asString() : dataNode.path("Total").asString(null);
            String invoiceNumber = dataNode.hasNonNull("Cislo_faktury") ? dataNode.get("Cislo_faktury").asString() : dataNode.path("Invoice_Number").asString(null);
            String dueDate = dataNode.hasNonNull("Datum_splatnosti") ? dataNode.get("Datum_splatnosti").asString() : dataNode.path("Due_Date").asString(null);
            String customer = dataNode.hasNonNull("Odberatel") ? dataNode.get("Odberatel").asString() : dataNode.path("Customer").asString(null);
            String bank = dataNode.hasNonNull("Banka") ? dataNode.get("Banka").asString() : dataNode.path("Bank").asString(null);
            String description = dataNode.hasNonNull("Popis") ? dataNode.get("Popis").asString() : dataNode.path("Description").asString(null);

            Map<String, Map<String, String>> goodsMap = new HashMap<>();
            JsonNode goodsNode = dataNode.hasNonNull("Zbozi") ? dataNode.get("Zbozi") : dataNode.path("Goods");

            if (goodsNode != null && goodsNode.isObject()) {

                goodsNode.properties().forEach(entry -> {
                    String itemName = entry.getKey();
                    JsonNode detailsNode = entry.getValue();
                    Map<String, String> detailsMap = new HashMap<>();
                    if (detailsNode.isObject()) {
                        detailsNode.properties().forEach(detailEntry -> {
                            detailsMap.put(detailEntry.getKey(), detailEntry.getValue().asText());
                        });
                    }
                    goodsMap.put(itemName, detailsMap);
                });
            }
            Invoice invoice = new Invoice();

            invoice.setInvoiceNumber(invoiceNumber);
            invoice.setInvoiceDate(invoiceDate);
            invoice.setDueDate(dueDate);
            invoice.setSeller(seller);
            invoice.setCustomer(customer);
            invoice.setTotalPrice(totalPrice);
            invoice.setPaymentMethod(paymentMethod);
            invoice.setBank(bank);
            invoice.setDescription(description);
            invoice.setGoods(goodsMap);

            invoiceRepository.save(invoice);
            return ResponseEntity.ok("Invoice saved " + invoice.getId());
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(e.getMessage());
        }
    }


    @GetMapping("/receipts")
    public ResponseEntity<List<Receipt>> getAllReceipts() {
        List<Receipt> allReceipts = receiptRepository.findAll();
        allReceipts.sort(new DocumentComparatorID());
        return ResponseEntity.ok(allReceipts);
    }

    @GetMapping("/invoices")
    public ResponseEntity<List<Invoice>> getAllInvoices() {
        List<Invoice> invoices = invoiceRepository.findAll();
        invoices.sort(new DocumentComparatorID());
        return ResponseEntity.ok(invoices);
    }
}
