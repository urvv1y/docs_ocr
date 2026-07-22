package com.example.demo;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
class DemoApplicationTests {

	@Autowired
	private MockMvc mockMvc;
	@Test
	void contextLoads() {
	}

	@Test
	void testGetReceiptsEndpointReturnsOk() throws Exception {
		mockMvc.perform(get("/api/receipts"))
				.andExpect(status().isOk());
	}

	@Test
	void testGetInvoiceEndpointReturnsOk() throws Exception {
		mockMvc.perform(get("/api/invoices")).andExpect(status().isOk());
	}

}
