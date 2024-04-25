library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

Library xpm;
use xpm.vcomponents.all;

entity axi4s_fifo_simple_v1_0 is
	generic (
		-- Users to add parameters here

      G_FIFO_DEPTH          : positive := 32;
      G_FIFO_TYPE           : string   := "auto";
      G_FIFO_CASCADE_HEIGHT : natural  := 0;
      G_FIFO_READ_LATENCY   : positive := 1;

		-- User parameters ends
		-- Do not modify the parameters beyond this line


		-- Parameters of Axi Slave Bus Interface S00_AXI
		C_S00_AXI_DATA_WIDTH	: integer	:= 32;
		C_S00_AXI_ADDR_WIDTH	: integer	:= 4;

		-- Parameters of Axi Slave Bus Interface S00_AXIS
		C_S00_AXIS_TDATA_WIDTH	: integer	:= 32
	);
	port (
		-- Users to add ports here

        overflow : out std_logic;

		-- User ports ends
		-- Do not modify the ports beyond this line


		-- Ports of Axi Slave Bus Interface S00_AXI
		s00_axi_aclk	   : in std_logic;
		s00_axi_aresetn	: in std_logic;
		s00_axi_awaddr	   : in std_logic_vector(C_S00_AXI_ADDR_WIDTH-1 downto 0);
		s00_axi_awprot	   : in std_logic_vector(2 downto 0);
		s00_axi_awvalid	: in std_logic;
		s00_axi_awready	: out std_logic;
		s00_axi_wdata	   : in std_logic_vector(C_S00_AXI_DATA_WIDTH-1 downto 0);
		s00_axi_wstrb	   : in std_logic_vector((C_S00_AXI_DATA_WIDTH/8)-1 downto 0);
		s00_axi_wvalid	   : in std_logic;
		s00_axi_wready	   : out std_logic;
		s00_axi_bresp	   : out std_logic_vector(1 downto 0);
		s00_axi_bvalid	   : out std_logic;
		s00_axi_bready   	: in std_logic;
		s00_axi_araddr   	: in std_logic_vector(C_S00_AXI_ADDR_WIDTH-1 downto 0);
		s00_axi_arprot	   : in std_logic_vector(2 downto 0);
		s00_axi_arvalid	: in std_logic;
		s00_axi_arready	: out std_logic;
		s00_axi_rdata	   : out std_logic_vector(C_S00_AXI_DATA_WIDTH-1 downto 0);
		s00_axi_rresp	   : out std_logic_vector(1 downto 0);
		s00_axi_rvalid   	: out std_logic;
		s00_axi_rready	   : in std_logic;

		-- Ports of Axi Slave Bus Interface S00_AXIS
		s00_axis_aclk	   : in std_logic;
		s00_axis_aresetn	: in std_logic;
		s00_axis_tready	: out std_logic;
		s00_axis_tdata	   : in std_logic_vector(C_S00_AXIS_TDATA_WIDTH-1 downto 0);
		s00_axis_tvalid	: in std_logic
	);
end axi4s_fifo_simple_v1_0;

architecture arch_imp of axi4s_fifo_simple_v1_0 is

	-- component declaration
	component axi4s_fifo_simple_v1_0_S00_AXI is
		generic (
		C_S_AXI_DATA_WIDTH	: integer	:= 32;
		C_S_AXI_ADDR_WIDTH	: integer	:= 4
		);
		port (
		O_FIFO_RD_EN    : out std_logic;
        I_FIFO_RD_DATA  : in  std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0);
        I_FIFO_RD_VALID : in  std_logic;
        I_FIFO_EMPTY    : in std_logic;
        I_FIFO_OVERFLOW : in std_logic;
      
		S_AXI_ACLK	    : in std_logic;
		S_AXI_ARESETN	 : in std_logic;
		S_AXI_AWADDR	 : in std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0);
		S_AXI_AWPROT	 : in std_logic_vector(2 downto 0);
		S_AXI_AWVALID	 : in std_logic;
		S_AXI_AWREADY	 : out std_logic;
		S_AXI_WDATA	    : in std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0);
		S_AXI_WSTRB	    : in std_logic_vector((C_S_AXI_DATA_WIDTH/8)-1 downto 0);
		S_AXI_WVALID	 : in std_logic;
		S_AXI_WREADY	 : out std_logic;
		S_AXI_BRESP	    : out std_logic_vector(1 downto 0);
		S_AXI_BVALID	 : out std_logic;
		S_AXI_BREADY	 : in std_logic;
		S_AXI_ARADDR	 : in std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0);
		S_AXI_ARPROT	 : in std_logic_vector(2 downto 0);
		S_AXI_ARVALID	 : in std_logic;
		S_AXI_ARREADY	 : out std_logic;
		S_AXI_RDATA	    : out std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0);
		S_AXI_RRESP	    : out std_logic_vector(1 downto 0);
		S_AXI_RVALID	 : out std_logic;
		S_AXI_RREADY	 : in std_logic
		);
	end component axi4s_fifo_simple_v1_0_S00_AXI;

	-- SIGNALS -------------------------------------------------------------------
	
	signal fifo_rst         : std_logic;
	signal fifo_rd_valid    : std_logic;
	signal fifo_rd_data     : std_logic_vector(C_S00_AXI_DATA_WIDTH-1 downto 0);
	signal fifo_empty       : std_logic;
	signal fifo_almost_full : std_logic;
	signal fifo_rd_en       : std_logic;
	signal fifo_overflow    : std_logic;
	
begin

-- Instantiation of Axi Bus Interface S00_AXI
axi4s_fifo_simple_v1_0_S00_AXI_inst : axi4s_fifo_simple_v1_0_S00_AXI
	generic map (
		C_S_AXI_DATA_WIDTH	=> C_S00_AXI_DATA_WIDTH,
		C_S_AXI_ADDR_WIDTH	=> C_S00_AXI_ADDR_WIDTH
	)
	port map (
	    O_FIFO_RD_EN    => fifo_rd_en,
	    I_FIFO_RD_DATA  => fifo_rd_data,
	    I_FIFO_RD_VALID => fifo_rd_valid,
	    I_FIFO_EMPTY    => fifo_empty,
	    I_FIFO_OVERFLOW => fifo_overflow,
	   
		S_AXI_ACLK	   => s00_axi_aclk,
		S_AXI_ARESETN	=> s00_axi_aresetn,
		S_AXI_AWADDR	=> s00_axi_awaddr,
		S_AXI_AWPROT	=> s00_axi_awprot,
		S_AXI_AWVALID	=> s00_axi_awvalid,
		S_AXI_AWREADY	=> s00_axi_awready,
		S_AXI_WDATA	   => s00_axi_wdata,
		S_AXI_WSTRB	   => s00_axi_wstrb,
		S_AXI_WVALID	=> s00_axi_wvalid,
		S_AXI_WREADY	=> s00_axi_wready,
		S_AXI_BRESP	   => s00_axi_bresp,
		S_AXI_BVALID	=> s00_axi_bvalid,
		S_AXI_BREADY	=> s00_axi_bready,
		S_AXI_ARADDR	=> s00_axi_araddr,
		S_AXI_ARPROT	=> s00_axi_arprot,
		S_AXI_ARVALID	=> s00_axi_arvalid,
		S_AXI_ARREADY	=> s00_axi_arready,
		S_AXI_RDATA  	=> s00_axi_rdata,
		S_AXI_RRESP	   => s00_axi_rresp,
		S_AXI_RVALID	=> s00_axi_rvalid,
		S_AXI_RREADY	=> s00_axi_rready
	);

	-- Add user logic here

   Fifo_Proc : process(s00_axis_aclk)
   begin
      if rising_edge(s00_axis_aclk) then
         fifo_rst        <= not s00_axis_aresetn;
         s00_axis_tready <= (not fifo_almost_full) and s00_axis_aresetn;
      end if;
   end process Fifo_Proc;

   xpm_fifo_sync_inst : xpm_fifo_sync
   generic map (
      CASCADE_HEIGHT      => G_FIFO_CASCADE_HEIGHT,        -- DECIMAL
      DOUT_RESET_VALUE    => "0",      -- String
      ECC_MODE            => "no_ecc", -- String
      FIFO_MEMORY_TYPE    => G_FIFO_TYPE, -- String
      FIFO_READ_LATENCY   => G_FIFO_READ_LATENCY,        -- DECIMAL
      FIFO_WRITE_DEPTH    => G_FIFO_DEPTH, -- DECIMAL
      FULL_RESET_VALUE    => 0,        -- DECIMAL
      PROG_EMPTY_THRESH   => 3,       -- DECIMAL
      PROG_FULL_THRESH    => G_FIFO_DEPTH-2, -- DECIMAL
      RD_DATA_COUNT_WIDTH => positive(log2(real(G_FIFO_DEPTH))) + 1, -- DECIMAL
      READ_DATA_WIDTH     => 32,       -- DECIMAL
      READ_MODE           => "std",    -- String
      SIM_ASSERT_CHK      => 0,        -- DECIMAL; 0=disable simulation messages, 1=enable simulation messages
      USE_ADV_FEATURES    => "1919",   -- String
      WAKEUP_TIME         => 0,        -- DECIMAL
      WRITE_DATA_WIDTH    => 32,       -- DECIMAL
      WR_DATA_COUNT_WIDTH => positive(log2(real(G_FIFO_DEPTH))) + 1         -- DECIMAL
   )
   port map (
      almost_empty  => open,
      almost_full   => fifo_almost_full,
      data_valid    => fifo_rd_valid,
      dout          => fifo_rd_data,
      empty         => fifo_empty,
      full          => open,
      overflow      => fifo_overflow,
      wr_ack        => open,
      din           => s00_axis_tdata,
      injectdbiterr => '0',
      injectsbiterr => '0',
      rd_en         => fifo_rd_en,
      rst           => fifo_rst,
      sleep         => '0',
      wr_clk        => s00_axis_aclk,
      wr_en         => s00_axis_tvalid
   );
   
   Fifo_Overflow_Proc : process (s00_axis_aclk)
   begin
      if rising_edge(s00_axis_aclk) then
         overflow <= fifo_overflow;
      end if;
   end process Fifo_Overflow_Proc;

	-- User logic ends

end arch_imp;
