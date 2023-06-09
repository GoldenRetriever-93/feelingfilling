package com.example.billing.data.loggingDB.document;

import lombok.*;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.config.EnableMongoAuditing;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.LocalDateTime;
@Setter
@Getter
@NoArgsConstructor
@Document(collection = "cancellation")
@AllArgsConstructor
@Builder
public class CancellationLogDocument {
    @Id
    private String _id;
    private int userId;
    private String serviceName;
    private int serviceUserId;
    private String sid;
    private long balance;
    private String status;
    private int orderId;
    private String tid;
    private String aid;
    private int cancellationId;
    private String cancellationMethod;
    private int cancellationAmount;
    @CreatedDate
    private LocalDateTime createdDate;
}
