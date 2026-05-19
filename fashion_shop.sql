-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th5 19, 2026 lúc 07:50 PM
-- Phiên bản máy phục vụ: 10.4.32-MariaDB
-- Phiên bản PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Cơ sở dữ liệu: `fashion_shop`
--

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `orders`
--

CREATE TABLE `orders` (
  `id` int(11) NOT NULL,
  `fullname` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `phone` varchar(50) NOT NULL,
  `address` text NOT NULL,
  `total_amount` decimal(12,2) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `order_items`
--

CREATE TABLE `order_items` (
  `id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `unit_price` decimal(12,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `products`
--

CREATE TABLE `products` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `price` decimal(12,2) NOT NULL,
  `stock` int(11) NOT NULL,
  `category` varchar(100) NOT NULL,
  `description` text NOT NULL,
  `image` varchar(500) NOT NULL,
  `is_featured` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `products`
--

INSERT INTO `products` (`id`, `name`, `price`, `stock`, `category`, `description`, `image`, `is_featured`, `created_at`) VALUES
(1, 'Áo sơ mi nam công sở dài tay', 350000.00, 100, 'Áo', 'Áo sơ mi chất liệu bamboo cao cấp, chống nhăn, thoáng khí, form dáng slim-fit tôn dáng lịch lãm.', 'https://example.com/ao-so-mi-nam.jpg', 1, '2026-05-19 23:18:57'),
(2, 'Quần tây âu nữ dáng suông ống rộng', 280000.00, 80, 'Quần', 'Quần tây dáng suông lưng cao, chất vải tuyết mưa dày dặn, thích hợp đi làm, đi chơi.', 'https://example.com/quan-tay-nu.jpg', 0, '2026-05-19 23:18:57'),
(3, 'Váy hoa nhí dáng dài cổ chữ V', 420000.00, 45, 'Váy', 'Váy voan tơ mềm mại có lót trong, họa tiết hoa nhí vintage ngọt ngào, bo eo nhẹ nhàng.', 'https://example.com/vay-hoa-nhi.jpg', 1, '2026-05-19 23:18:57'),
(4, 'Áo khoác Bomber nỉ ngoại unisex', 390000.00, 60, 'Áo khoác', 'Áo khoác kiểu dáng bomber năng động, chất nỉ dày dặn, tay phối màu hot trend cho nam nữ.', 'https://example.com/ao-bomber.jpg', 1, '2026-05-19 23:18:57'),
(5, 'Quần short jeans nam rách gối nhẹ', 220000.00, 120, 'Quần', 'Chất denim co giãn nhẹ, màu xanh bạc cá tính, dễ dàng phối cùng áo thun, áo polo.', 'https://example.com/short-jeans-nam.jpg', 0, '2026-05-19 23:18:57'),
(6, 'Áo hoodie nỉ bông form rộng oversized', 290000.00, 150, 'Áo', 'Áo hoodie có mũ trùm dày dặn, lót nỉ bông ấm áp, thích hợp cho thời tiết thu đông.', 'https://example.com/ao-hoodie.jpg', 1, '2026-05-19 23:18:57'),
(7, 'Chân váy tennis xếp ly ngắn có quần trong', 180000.00, 95, 'Váy', 'Chân váy ngắn xếp ly đều đặn, chất tuyết mưa đứng form, có sẵn quần bảo hộ bên trong tiện lợi.', 'https://example.com/chan-vay-tennis.jpg', 0, '2026-05-19 23:18:57'),
(8, 'Áo polo nam cotton cá sấu phối sọc', 260000.00, 110, 'Áo', 'Chất vải cá sấu co giãn 4 chiều, thấm hút mồ hôi tốt, cổ bẻ thanh lịch phù hợp mọi hoàn cảnh.', 'https://example.com/ao-polo-nam.jpg', 1, '2026-05-19 23:18:57'),
(9, 'Quần jogger thun nam nữ dáng thể thao', 195000.00, 200, 'Quần', 'Thiết kế bo gấu năng động, chất thun cotton dày dặn, có túi khóa zip hai bên tiện lợi.', 'https://example.com/quan-jogger.jpg', 0, '2026-05-19 23:18:57'),
(10, 'Đầm dạ hội trễ vai dáng ôm quyến rũ', 650000.00, 20, 'Váy', 'Thiết kế trễ vai sang trọng, xẻ tà đùi cao, chất vải satin bóng nhẹ tôn dáng tối đa cho các buổi tiệc.', 'https://example.com/dam-da-hoi.jpg', 1, '2026-05-19 23:18:57'),
(11, 'Áo len nữ cổ lọ dệt kim basic', 240000.00, 70, 'Áo', 'Chất len dệt kim mềm mịn, co giãn ôm sát cơ thể giữ ấm tốt, không bị xù lông khi giặt.', 'https://example.com/ao-len-co-lo.jpg', 0, '2026-05-19 23:18:57'),
(12, 'Quần jean baggy nữ cạp cao rách gối', 310000.00, 85, 'Quần', 'Form quần baggy thoải mái, che khuyết điểm chân tốt, chất bò dày dặn không phai màu.', 'https://example.com/jean-baggy-nu.jpg', 1, '2026-05-19 23:18:57'),
(13, 'Bộ đồ ngủ Pijama lụa satin họa tiết dài tay', 250000.00, 130, 'Đồ ngủ', 'Chất lụa satin cao cấp bóng mượt, mát lịm, đường may tỉ mỉ, họa tiết dễ thương sắc nét.', 'https://example.com/pijama-lua.jpg', 0, '2026-05-19 23:18:57'),
(14, 'Áo khoác Blazer nữ 2 lớp dáng rộng', 450000.00, 40, 'Áo khoác', 'Áo blazer thiết kế có đệm vai nhẹ, bên trong lót lụa mềm mại, dễ phối đồ theo phong cách hiện đại.', 'https://example.com/blazer-nu.jpg', 1, '2026-05-19 23:18:57'),
(15, 'Quần short đùi nam dây rút lưng thun', 160000.00, 140, 'Quần', 'Vải đũi xước tự nhiên siêu nhẹ và mát, thích hợp mặc ở nhà, đi biển hoặc dạo phố ngày hè.', 'https://down-vn.img.susercontent.com/file/vn-11134207-7ra0g-m9zn89binzvyb0@resize_w450_nl.webp', 0, '2026-05-19 23:18:57');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `reviews`
--

CREATE TABLE `reviews` (
  `id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `comment` text NOT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `is_admin` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `password_hash`, `is_admin`, `created_at`) VALUES
(1, 'Tuấn', 'tuantruong@gmail.com', '$2b$12$Qc.atobmNM0VoO3I7IOat.AnMoykLWtjpE1pcbD34EuwqtrDEfdmu', 0, '2026-05-19 22:52:33'),
(2, 'Admin Shop', 'admin@shop.com', '$2b$12$q7qqrf4RiVQvpx/ntiR1geyQuv.o7bqDP1GH8YVbPHls7gN3jg0ia', 1, '2026-05-19 22:59:31');

--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`id`);

--
-- Chỉ mục cho bảng `order_items`
--
ALTER TABLE `order_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `product_id` (`product_id`);

--
-- Chỉ mục cho bảng `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`id`);

--
-- Chỉ mục cho bảng `reviews`
--
ALTER TABLE `reviews`
  ADD PRIMARY KEY (`id`),
  ADD KEY `product_id` (`product_id`);

--
-- Chỉ mục cho bảng `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT cho các bảng đã đổ
--

--
-- AUTO_INCREMENT cho bảng `orders`
--
ALTER TABLE `orders`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `order_items`
--
ALTER TABLE `order_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `products`
--
ALTER TABLE `products`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT cho bảng `reviews`
--
ALTER TABLE `reviews`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Các ràng buộc cho các bảng đã đổ
--

--
-- Các ràng buộc cho bảng `order_items`
--
ALTER TABLE `order_items`
  ADD CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `order_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `reviews`
--
ALTER TABLE `reviews`
  ADD CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
